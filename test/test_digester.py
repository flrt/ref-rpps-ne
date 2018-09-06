import logging
import unittest

import digester
from easy_atom import helpers


class TestDigester(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("utest")

    def test_equal_data(self):
        self.logger.info("  TEST test_equal_data")

        d = digester.Digester()
        dig1 = d.digest("test/files/PS_LibreAcces_Dipl_AutExerc_201807300827.txt")
        self.logger.info(len(dig1))

        dig2 = d.load_digest(
            "test/files/PS_LibreAcces_Dipl_AutExerc_201807300827.txt.sha"
        )
        self.logger.info(len(dig2))

        self.assertEqual(len(dig1), len(dig2))


if __name__ == "__main__":
    loggers = helpers.stdout_logger(["utest", "digester"], logging.INFO)

    unittest.main()
