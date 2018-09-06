import logging
import os.path
import unittest

import differentia
from easy_atom import helpers


class TestDiff(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("utest")

    def test_equal_data(self):
        self.logger.info("  TEST test_equal_data")

        d = differentia.Diff(
            "test/files/PS_LibreAcces_Dipl_AutExerc_201807300827.txt",
            storage_dir="test/files",
        )
        result = d.find_diff(
            os.path.abspath("test/files/PS_LibreAcces_Dipl_AutExerc_201807300827.txt")
        )

        self.assertEqual(len(result), 0)

    def test_1diff_data(self):
        self.logger.info("  TEST test_1diff_data")

        d = differentia.Diff(
            "test/files/PS_LibreAcces_Dipl_AutExerc_201807300827.txt",
            storage_dir="test/files",
        )
        result = d.find_diff(
            os.path.abspath(
                "test/files/PS_LibreAcces_Dipl_AutExerc_201807300827_1DIFF.txt"
            )
        )
        self.logger.info(result)

        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    loggers = helpers.stdout_logger(["utest", "digester", "differentia"], logging.INFO)

    unittest.main()
