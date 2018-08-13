import datetime
import logging
import os.path
from datetime import datetime as dt

from easy_atom import atom
from easy_atom import content


class Info:
    def __init__(self, properties):
        self.logger = logging.getLogger("info")
        self.pub_url = ""
        self.init_properties(properties)

    def init_properties(self, properties):
        """
            properties bootstrap

        :param properties: properties object
        :return: -
        """
        try:
            self.pub_url = properties.pub.url_base
            if not self.pub_url.endswith("/"):
                self.pub_url += "/"
        except AttributeError as ae:
            self.logger.warning("[config] No/Wrong pub.url_base properties : %s" % ae)

    def make_link(self, parent, text, filename):
        if filename:
            # Add an <a> element to parent
            content.xmlelt(
                parent,
                "a",
                f"{text}: {os.path.basename(filename)}",
                {"href": self.pub_url + filename},
            )
        else:
            # nothing to do
            pass

    def feed_info(self, data_tracks):
        """
        Get Information from data to populate feed

        :param data_tracks: data about configured tracks to follow

        """
        self.logger.debug(f"feed_info, {len(data_tracks)} data tracks")
        self.logger.debug(f"feed_info, {data_tracks} ")

        #

        # root XML element
        root = content.xmlelt(None, "div")
        # content.xmlelt(root, "h1", data_tracks["title"])

        # Link to files
        content.xmlelt(root, "h3", "Fichiers à télécharger")
        ul = content.xmlelt(root, "ul")

        if data_tracks["diff_data_filename"]:
            self.make_link(
                content.xmlelt(ul, "li"),
                "fichier de données (delta)",
                data_tracks["diff_data_filename"],
            )
        if data_tracks["diff_index_filename"]:
            self.make_link(
                content.xmlelt(ul, "li"),
                "fichier d'index des différences",
                data_tracks["diff_index_filename"],
            )

        content.xmlelt(root, "h3", "Statistiques")

        for track in data_tracks["tracks"]:
            self.logger.debug("------ > ------- ")
            self.logger.debug(track)
            content.xmlelt(root, "h2", track["title"])
            # data tracks
            ul = content.xmlelt(root, "ul")

            for data in track["values"]:
                content.xmlelt(ul, "li", f"{data['key']} : {data['val']}")

        self.logger.debug(f"Produced feed infos {content.xml2text(root)}")
        return root

    def to_rss(self, xmlinfos, data_date, data_files):
        self.logger.debug(f"To RSS, {len(xmlinfos)} blocks")

        root = content.xmlelt(None, "div")
        [root.append(inf) for inf in xmlinfos]

        info = dict(
            html=content.xml2text(root, atom.Feed.FEED_ENCODING, xml_decl=False),
            files=list(map(lambda x: self.pub_url + os.path.basename(x), data_files)),
            title=f"Mise à jour RPPS du {data_date}",
            id=f"rpps{data_date}",
            date=dt.now(datetime.timezone.utc).isoformat(sep="T"),
            summary=f"Informations sur la publication RPPS du {data_date}",
        )
        return info
