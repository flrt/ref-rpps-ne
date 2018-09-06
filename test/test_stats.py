import logging
import unittest

import practitioner
import pandas

import easy_atom.helpers as helpers

"""
df=pandas.read_csv(tfile, delimiter=";", names=KEYS, header=0, index_col=False)
df.loc(df.identifiant_pp==10005831911)
mss_providers=df.adresse_bal_mssante.str.split('@',expand=True).get(1)

mss_providers.where(mss_providers=='ch-larochelle.mssante.fr').dropna().count()
mss_providers.where(mss_providers.str.contains('ch-aix')).dropna()

"""


class TestStats(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("utest")

    @staticmethod
    def parse_csv(filename):
        data = []
        nline = 1
        with open(filename, "r") as fin:
            for line in fin.readlines():
                vals = line.replace('"', "").split("|")
                if nline > 1:
                    data.append(dict(zip(practitioner.RPPS.KEYS_MSSANTE, vals[:-1])))
                nline = nline + 1
        return data

    def test_count(self):
        df = pandas.read_csv(
            "/opt/test/test/files/Extraction_Correspondance_MSSante_201807310813.txt",
            delimiter="|",
            names=practitioner.RPPS.KEYS_MSSANTE,
            header=0,
            index_col=False,
        )

        self.logger.info("nunique : %d" % df["identifiant_pp"].nunique())
        self.logger.info("MSSante : %d" % df["adresse_bal"].nunique())
        self.logger.info("MSSante total : %d" % len(df))

        mss_providers = df.adresse_bal.str.split("@", expand=True).get(1)

        self.logger.info("Nb MSS : %d" % len(mss_providers.unique()))
        self.logger.info("Nb by provider : %d" % len(mss_providers.value_counts()))

        self.assertEqual(len(df), 136693)
        self.assertEqual(116797, df["identifiant_pp"].nunique())
        self.assertEqual(136166, df["adresse_bal"].nunique())


if __name__ == "__main__":
    loggers = helpers.stdout_logger(["utest"], logging.INFO)

    unittest.main()
