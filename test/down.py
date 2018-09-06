import json
import logging
import unittest
from collections import namedtuple

import practitioner
from easy_atom import helpers


class TestDownload(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("utest")
        config_dict = """
            {
                "URL" : "https://service.annuaire.sante.fr/annuaire-sante-webservices/V300/services/extraction/PS_LibreAcces",
                "local": {
                            "last_check": "201805260809",
                            "storage": "test/files"
                }
            }
            """
        self.config_1 = json.loads(
            config_dict,
            object_hook=lambda d: namedtuple("JDATA", d.keys())(*d.values()),
        )

        config_dict = """
            {
                "URL" : "https://service.annuaire.sante.fr/annuaire-sante-webservices/V300/services/extraction/PS_LibreAcces",
                "local": {
                            "last_check": "202808100809",
                            "storage": "test/files"
                }
            }
            """

        self.config_2 = json.loads(
            config_dict,
            object_hook=lambda d: namedtuple("JDATA", d.keys())(*d.values()),
        )

    def test_download(self):
        self.logger.info("Test - test_download")
        d = practitioner.RPPS(properties=self.config_1)
        newfilename = d.retrieve_current()
        self.assertIsNotNone(newfilename)

    def test_no_download(self):
        self.logger.info("Test - test_no_download")

        d = practitioner.RPPS(properties=self.config_2)

        newfilename = d.retrieve_current()
        self.assertIsNone(newfilename)

    def test_newer(self):
        self.logger.info("Test - test_newer")
        d = practitioner.RPPS(properties=self.config_1)

        self.assertTrue(d.is_newer("PS_LibreAcces_201808011050.zip"))
        self.assertFalse(d.is_newer("PS_LibreAcces_201408011050.zip"))

    def test_root_filename(self):
        d = practitioner.RPPS(properties=self.config_1)
        fn = "PS_LibreAcces_Dipl_AutExerc_201807300827.txt"

        self.assertEqual(d.root_data_filename(fn), "PS_LibreAcces_Dipl_AutExerc")


if __name__ == "__main__":
    loggers = helpers.stdout_logger(["utest", "downloader"], logging.DEBUG)

    unittest.main()
