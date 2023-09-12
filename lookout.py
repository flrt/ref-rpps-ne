#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

    Main App
    Detects if a newer file is available, process it

"""
__author__ = "Frederic Laurent"
__version__ = "1.0"
__copyright__ = "Copyright 2018, Frederic Laurent"
__license__ = "MIT"

import argparse
import logging
import os.path
import sys

import differentia
import info
import practitioner


from easy_atom import action
from easy_atom import atom
from easy_atom import helpers


class App:
    """
        Main App
    """

    DEFAULT_DIR = "default"

    def __init__(self, config):
        """
            Init class, loads config file
            :param config_filename: configration file name
        """

        self.logger = logging.getLogger("app")
        self.logger.info("Config : %s" % config)

        # domain rpps or mssante. computed by naming convention of config files
        self.domain = None

        self.cfg_filename = config
        self.config_dir = None

        self.previous_filename = {}
        self.data_files = []
        self.rss_filename = None
        self.rss_history = None
        self.stats_filename = None
        self.feed = None

        self.init_properties()
        self.logger.info(self.properties)

        self.init_feed()

        self.rpps_data = practitioner.RPPS(properties=self.properties)

    def config_filename(self, config):
        """
            locates the config filename. If the argument is found, takes it.
            Otherwise, takes the same filename (default content) in defaut directory

        :param config: config filename
        :return: good config filename
        """
        cfg_filename = config
        if not os.path.exists(os.path.abspath(cfg_filename)):
            cfg_filename = os.path.join(App.DEFAULT_DIR, os.path.basename(config))
            self.logger.info(f"No config file {config}. Using default {cfg_filename}")
        return cfg_filename

    def init_properties(self):
        """
            Loads properties
            Set the config directory depending of the existance of the config file

        :return:
        """
        self.properties = helpers.json_to_object(
            self.config_filename(self.cfg_filename)
        )

        if "rpps" in os.path.basename(self.cfg_filename):
            self.domain = "rpps"
        elif "mssante" in os.path.basename(self.cfg_filename):
            self.domain = "mssante"
        else:
            self.domain = "unk"

        try:
            self.rss_filename = os.path.join(
                self.properties.local.storage,
                self.properties.local.rss_updates_filename,
            )
        except AttributeError as attr_err:
            self.logger.info("[config] Don't produce RSS (%s)" % attr_err)

        try:
            self.stats_filename = os.path.join(
                self.properties.local.storage, self.properties.tracks.stats.filename
            )
        except AttributeError as attr_err:
            self.logger.info("[config] Don't produce Stats (%s)" % attr_err)

        try:
            for k in self.properties.local.data._fields:
                self.logger.info(k)
                self.previous_filename[k] = getattr(self.properties.local.data, k)
        except AttributeError as attr_err:
            self.logger.info("[config] No previous file (%s)" % attr_err)

        try:
            self.rss_history = self.properties.local.rss_history
            self.logger.info(
                f"Max History = {self.rss_history} ({type(self.rss_history)})"
            )
        except AttributeError as attr_err:
            self.logger.info("[config] No RSS history limit (%s)" % attr_err)

    def init_feed(self):
        """
            Init feed.
            If the classical config name (naming convention) is found, no special is done
            If the config file name is not found, take the same filename but in the default directory
            and loads it

        :return: -
        """
        self.feed = atom.Feed(self.domain, self.properties.pub.feed_base)

        cfg_feed_fn = self.feed.get_config_filename()
        cfg_feed_fn2 = self.config_filename(cfg_feed_fn)
        self.logger.debug(f"Feed config {cfg_feed_fn} - {cfg_feed_fn2}")
        self.feed.load_config(self.config_filename(cfg_feed_fn))

    def make_diff_data_filename(self, fn):
        """
            Builds the name of the data file of difference
        :param fn: original file name
        :return: diff file name
        """
        data_filename = None
        try:
            if self.properties.local.save_diff_index:
                data_filename = os.path.join(
                    self.properties.local.storage, f"new_{os.path.basename(fn)}.diff"
                )
                self.data_files.append(data_filename)
        except AttributeError as attr_err:
            self.logger.debug(f"[config] Don't save diff data ({attr_err}) for {fn} ")
        self.logger.debug(f"make_diff_data_filename -> {data_filename}")
        return data_filename

    def make_diff_index_filename(self, fn):
        """
            Builds the name of the index file of differences
        :param fn: original file name
        :return: index file name
        """
        data_filename = None
        try:
            if self.properties.local.save_diff_index:
                data_filename = os.path.join(
                    self.properties.local.storage, f"index_{os.path.basename(fn)}.csv"
                )
                self.data_files.append(data_filename)
        except AttributeError as attr_err:
            self.logger.debug(f"[config] Don't save diff index ({attr_err}) for {fn} ")
        self.logger.debug(f"make_diff_index_filename -> {data_filename}")
        return data_filename

    def process(self, zipfile=None):
        """
            Download newer file (zip) if available
            Process data
             - unzip file
             - process each file
                - compute diff
                - extract data
             - produce new information files
             - produce RSS feed if configured
        """

        self.logger.debug(f"Start... (zipfile={zipfile})")
        try:
            _zip = None
            if zipfile:
                # use arg filename, local file
                if not os.path.exists(zipfile):
                    self.logger.error(f"File {zipfile} not found !")
                    sys.exit(1)
                _zip = zipfile
            else:
                # download new file if available
                _zip = self.rpps_data.retrieve_current()

            self.logger.info(f"Zip data file : {_zip}")
            # compute Zip file
            if _zip and self.rpps_data.is_newer(_zip):
                self.logger.debug(f"Unzip data file : {_zip}")

                info_blocks = []
                for _new_data_file in self.rpps_data.unzip(
                    _zip, self.properties.local.storage
                ):
                    # compute file
                    self.logger.info(f"Compute file {_new_data_file} ")
                    # get root name
                    _root_fn = self.rpps_data.root_data_filename(
                        os.path.basename(_new_data_file)
                    )
                    # get previous filename
                    _previous = self.previous_filename[_root_fn]

                    self.logger.debug(f"File type : {_root_fn} - previous {_previous}")
                    # compute diff
                    diff = differentia.Diff(
                        _previous, storage_dir=self.properties.local.storage
                    )
                    diff_list = diff.find_diff(os.path.abspath(_new_data_file))
                    self.logger.info(f"Diff count : {len(diff_list)}")

                    # update last computed file
                    self.previous_filename[_root_fn] = _new_data_file

                    # get the date included in the filename
                    _remote_fn, _date = self.rpps_data.extract_data_filename(_zip)
                    self.rpps_data.set_data_date(self.rpps_data.parse_date(_date))
                    # extract informations
                    data_tracks = {
                        "filename": _new_data_file,
                        "diff_data_filename": self.make_diff_data_filename(
                            _new_data_file
                        ),
                        "diff_index_filename": self.make_diff_index_filename(
                            _new_data_file
                        ),
                        "date": self.rpps_data.data_date,
                        "tracks": self.rpps_data.extract_data(
                            _new_data_file, diff_list
                        ),
                    }
                    self.logger.debug(f"data_tracks {data_tracks}")

                    self.rpps_data.save_diff_files(
                        data_tracks["diff_data_filename"],
                        data_tracks["diff_index_filename"],
                        diff_list,
                    )
                    info_blocks.append(data_tracks)

                    # add tracks file names in produced data files
                    self.logger.debug(f"Data files : {self.rpps_data.data_files}")
                    self.logger.debug(f"Data tracks : {data_tracks}")

                    lst = self.rpps_data.save_tracks(data_tracks)
                    self.data_files.extend(lst)

                # update RSS
                self.make_rss(info_blocks)

                self.rpps_data.update_last_check_date(_zip)
                self.logger.debug(f"Last Check date : {self.rpps_data.last_check_date}")

                self.save_config()
            else:
                self.logger.info(
                    f"No newer file (post {self.rpps_data.last_check_date})"
                )

        except AttributeError as attr_err:
            self.logger.info(f"[config] Wrong/No data file name : {attr_err}")

    def make_rss(self, info_blocks):
        """
            Produces RSS from
                - already saved informations
                - new data
        :param info_blocks: fresh data
        :return: -
        """
        if self.rss_filename:
            self.logger.debug(f"Loading RSS data feed : {self.rss_filename}")
            rpps_updates = helpers.load_json(self.rss_filename)
            if "updates" not in rpps_updates:
                rpps_updates = {"updates": []}

            self.logger.info(rpps_updates)
            inf = info.Info(self.properties)
            feed_info = list(map(lambda i: inf.feed_info(i), info_blocks))
            d = inf.to_rss(feed_info, self.rpps_data.data_date, self.data_files)

            self.logger.debug(f"Insert (top) history : {d}")
            rpps_updates["updates"].insert(0, d)

            if self.rss_history:
                rpps_updates["updates"] = rpps_updates["updates"][: self.rss_history]

            helpers.save_json(self.rss_filename, rpps_updates)

            # produce RSS/atom file
            result = self.feed.generate(rpps_updates["updates"])
            self.feed.save(result)
            self.feed.rss2()

    def statistics(self, txtfile):
        """
            Give some statistics (via log)
        :param txtfile: file containing data
        :return: -

        """

        data_tracks = {
            "filename": txtfile,
            "diff_data_filename": None,
            "diff_index_filename": None,
            "date": self.rpps_data.data_date,
            "tracks": self.rpps_data.extract_data(txtfile, []),
        }

        self.logger.debug(
            f" filename > {data_tracks['filename']} - history {data_tracks['history_flag']}"
        )

        for data in data_tracks:
            maxlen = max(list(map(lambda x: len(x["key"]), data["values"])))

            for val in data["values"]:
                # self.logger.info(f'  {val["key"]:{"<"}{maxlen}} = {val["val"]}')
                self.logger.info(
                    '  {mykey:{"<"}{width}} = {myvalue}'.format(
                        mykey=val["key"], myvalue=val["val"], width=maxlen
                    )
                )

    def save_config(self):
        """
            Save configuration file with new processed files
        :return: -
        """
        new_data_section = self.properties.local.data._replace(**self.previous_filename)

        new_local_section = self.properties.local._replace(
            data=new_data_section, last_check=self.rpps_data.last_check_date
        )
        new_props = self.properties._replace(local=new_local_section)
        helpers.object_to_json(new_props, self.cfg_filename)

    def upload_data(self, config):
        """
            Upload data files, according to parameters in config

            :param config: Configuration used to upload data on a server
        """

        self.logger.info("Upload data updates : %s" % self.data_files)
        act = action.UploadAction(conf_filename=config)
        act.process(self.data_files)

    def upload_feed(self, config):
        """
            Upload Feed file

            :param config: Configuration used to upload feed on a server
        """
        self.logger.info("Upload feeds updates")
        act = action.UploadAction(conf_filename=config)
        self.logger.debug(
            f"Files to upload : Atom={self.feed.feed_filename} RSS2={self.feed.rss2_filename}"
        )
        act.process([self.feed.feed_filename, self.feed.rss2_filename])


def main():
    """
        Main : process arguments and start App
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="fichier de parametres")
    parser.add_argument(
        "--feedftp", help="configuration FTP pour upload du flux ATOM, format JSON"
    )
    parser.add_argument(
        "--dataftp", help="configuration FTP pour upload des données, format JSON"
    )
    parser.add_argument(
        "--zip", help="Fichier ZIP contenant l'extraction RPPS ou MSSante"
    )
    parser.add_argument(
        "--txt",
        help="Fichier texte contenant l'extraction RPPS ou MSSante (pour stats)",
    )

    parser.add_argument("--stat", help="Affiche les stats")

    args = parser.parse_args()
    if args.config:
        app = App(args.config)

        if args.stat and args.txt and os.path.exists(args.txt):
            app.statistics(args.txt)

        else:
            app.process(args.zip)

            if args.dataftp and os.path.exists(args.dataftp):
                app.upload_data(args.dataftp)
            if args.feedftp and os.path.exists(args.feedftp):
                app.upload_feed(args.feedftp)
    else:
        sys.stdout.write("/!\\ Aucune action définie !\n\n")
        parser.print_help(sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    loggers = helpers.stdout_logger(
        [
            "downloader",
            "differentia",
            "app",
            "digester",
            "practitioner",
            "info",
            "feed",
        ],
        logging.DEBUG,
    )
    main()
