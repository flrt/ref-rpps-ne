import logging
import unittest

from easy_atom import helpers


class TestDiff(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("utest")

    def test_equal_data(self):
        self.logger.info("  TEST test_equal_data")
        prop = helpers.json_to_object("files/test-config.json")

        self.assertEqual(prop._fields, ("local", "pub", "tracks"))
        self.assertEqual(prop.pub._fields, ("url_base", "feed_base"))

    def test_alter(self):
        """
            alter values data_filename and zip_last_date
        :return: -
        """
        self.logger.info("  TEST test_alter")
        prop = helpers.json_to_object("files/test-config.json")

        # alter field
        __new_data_filename = "newdata.CSV"
        __new_check_date = "20181224235900"
        altered_local = prop.local._replace(
            data_filename=__new_data_filename, last_check=__new_check_date
        )

        newprops = prop._replace(local=altered_local)
        helpers.object_to_json(newprops, "files/test-config-alt.json")

        # reload
        prop2 = helpers.json_to_object("files/test-config-alt.json")
        self.assertEqual(prop2.local.data_filename, __new_data_filename)
        self.assertEqual(prop2.local.zip_last_date, __new_check_date)


if __name__ == "__main__":
    loggers = helpers.stdout_logger(["utest"], logging.INFO)

    unittest.main()
