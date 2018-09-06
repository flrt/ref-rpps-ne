import datetime
import json
import logging
import unittest
from collections import namedtuple

import practitioner
from easy_atom import helpers


class TestUnzip(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("utest")
        self.zipfilename = "test/files/PS_LibreAcces_201808011050.zip"

        config_dict = """
            {
                "URL" : "https://service.annuaire.sante.fr/annuaire-sante-webservices/V300/services/extraction/PS_LibreAcces",
                "local": {
                            "last_check": "201808011050",
                            "storage": "test/files"
                }
            }
            """

        self.config_1 = json.loads(
            config_dict,
            object_hook=lambda d: namedtuple("JDATA", d.keys())(*d.values()),
        )

    def test_unzip(self):
        start_date = datetime.datetime.now()

        d = practitioner.RPPS(properties=self.config_1)
        self.logger.debug("Extract to %s" % d.local_storage)

        _files = d.unzip(self.zipfilename, d.local_storage)

        end_date = datetime.datetime.now()

        delta = end_date - start_date
        self.logger.info("Start  : %s" % start_date.isoformat())
        self.logger.info("End    : %s" % end_date.isoformat())
        self.logger.info("Delta  : %s" % delta)

        self.logger.info(_files)

        self.assertEqual(len(_files), 3)


if __name__ == "__main__":
    loggers = helpers.stdout_logger(["utest"], logging.INFO)

    unittest.main()
