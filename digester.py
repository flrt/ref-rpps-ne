#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Make a digest of each line of a data file
    The resulting digest filename has the Digester.FILE_SUFFIX by default

"""
__author__ = "Frederic Laurent"
__version__ = "1.0"
__copyright__ = "Copyright 2017, Frederic Laurent"
__license__ = "MIT"

import argparse
import hashlib
import logging
import os.path
import codecs

try:
    from easy_atom import helpers
except ImportError:
    print(f"Erreur import - Atom")

class Digester:
    """
        File Digester

    """

    CHAR_FIELDS_SEP = ":"
    FILE_SUFFIX = ".sha"

    def __init__(self):
        self.logger = logging.getLogger("digester")
        self.data = []

    @staticmethod
    def sha_filename(filename):
        """
            Build digest filename
        :param filename: original filename
        :return: built filename
        """
        if not filename.endswith(Digester.FILE_SUFFIX):
            return "%s%s" % (filename, Digester.FILE_SUFFIX)
        else:
            return filename

    def digest(self, filename):
        """
            Make a digest file according to the data filename
        :param filename: filename of data
        :return: digest
        """
        shfn = self.sha_filename(filename)

        if os.path.exists(os.path.abspath(shfn)):
            self.load_data(filename)
            return self.load_digest(shfn)
        else:
            return self.make_digest(filename)

    def make_digest(self, filename):
        """
            Build digest map
        :param filename: data filename
        :return: digest map
        """
        self.logger.info("Make digest :> %s" % filename)
        data_sha = {}
        del self.data[:]

        with open(self.sha_filename(filename), "w") as fout:
            line_number = 0
            try:
                with codecs.open(filename, "r", "utf-8") as fin:
                    for line in fin.readlines():
                        digest = hashlib.sha256(line.encode("utf8")).hexdigest()
                        data_sha[digest] = line_number
                        self.data.append(line.strip())
                        fout.write("%d:%s\n" % (line_number, digest))
                        line_number += 1
            except OSError as oserr:
                self.logger.error(f"Error while loading {filename} : {str(oserr)}")
        return data_sha

    def load_digest(self, filename):
        """
            Load digest file
        :param filename:
        :return: digest data
        """
        self.logger.info("Load digest <: %s" % filename)

        data_sha = {}
        with open(filename, "r") as fin:
            for line in fin.readlines():
                vals = line.strip().split(Digester.CHAR_FIELDS_SEP)
                data_sha[vals[-1]] = int(vals[0])
        return data_sha

    def load_data(self, filename):
        """
            Load data file
        :param filename: file name
        :return: list of lines
        """
        self.logger.info("Load Data <: %s" % filename)
        del self.data[:]

        try:
            with codecs.open(filename, "r", "utf-8") as fin:
                for line in fin.readlines():
                    self.data.append(line.strip())
        except OSError as oserr:
            self.logger.error(f"Error while loading data {str(oserr)}")


if __name__ == "__main__":
    loggers = helpers.stdout_logger(["digester"], logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="data file")
    args = parser.parse_args()

    dig = Digester()
    dig.make_digest(args.file)
