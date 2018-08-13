#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

    Main App

"""
__author__ = "Frederic Laurent"
__version__ = "1.0"
__copyright__ = "Copyright 2018, Frederic Laurent"
__license__ = "MIT"

import argparse
import logging
import sys

import pandas

import practitioner
from easy_atom import helpers


class App:
    """
        Main App
    """

    def __init__(self, filename):
        self.logger = logging.getLogger("app")
        self.filename = filename

    def process(self, domain=None):
        self.logger.debug(f"Search {domain}... (file={self.filename}")
        # Read data
        df = pandas.read_csv(
            self.filename,
            delimiter="|",
            names=practitioner.RPPS.KEYS_MSSANTE,
            header=0,
            index_col=False,
        )

        df_domain = df[df.adresse_bal.str.match(f".*{domain}.*")]
        return df_domain.adresse_bal.drop_duplicates().values.tolist()

    def display(self, result):
        print(f"{len(result)} valueurs")
        for r in result:
            print(r)


def main():
    """
        Main : process arguments and start App
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", help="domaine a chercher")
    parser.add_argument("--txt", help="Fichier texte contenant l'extraction MSSante")

    args = parser.parse_args()
    if args.txt and args.domain:
        app = App(args.txt)
        result = app.process(args.domain)
        app.display(result)
    else:
        sys.stdout.write("/!\\ Aucune action définie !\n\n")
        parser.print_help(sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    loggers = helpers.stdout_logger(["app"], logging.DEBUG)
    main()
