import logging
import os
import os.path
import re
import sys
from datetime import datetime as dt

from easy_atom import helpers
import pandas

import practitioner

MSSANTE = [
    {
        "domains": {
            "title": "Domaines des CHU",
            "value": [
                "chu-amiens.mssante.fr",
                "chu-besancon.mssante.fr",
                "chu-bordeaux.mssante.fr",
                "chu-brest.mssante.fr",
                "chu-caen.mssante.fr",
                "chu-clermontferrand.mssante.fr",
                "chu-dijon.mssante.fr",
                "chu-grenoble.mssante.fr",
                "chru-lille.mssante.fr",
                "chu-limoges.mssante.fr",
                "chu-lyon.mssante.fr",
                "aphm.mssante.fr",
                "sante-martinique.mssante.fr",
                "hpdir-metz.mssante.fr",
                "chu-montpellier.mssante.fr",
                "chru-nancy.mssante.fr",
                "chu-nantes.mssante.fr",
                "chu-nice.mssante.fr",
                "chu-nimes.mssante.fr",
                "chr-orleans.mssante.fr",
                "aphp.mssante.fr",
                "guadeloupe.mssante.fr",
                "chu-poitiers.mssante.fr",
                "chu-reims.mssante.fr",
                "chu-rennes.mssante.fr",
                "chu-rouen.mssante.fr",
                "chu-st-etienne.mssante.fr",
                "chru-strasbourg.mssante.fr",
                "chu-toulouse.mssante.fr",
                "chu-tours.mssante.fr",
            ],
        },
        "filename": "chu-mssante.json",
        "name": "chu-mssante",
    },
    {
        "domains": {
            "title": "Domaines du GHT Bouches du Rhone",
            "value": [
                "aphm.mssante.fr",
                "ch-allauch.mssante.fr",
                "ch-aubagne.mssante.fr",
                "ch-laciotat.mssante.fr",
                "ch-salon.mssante.fr",
                "ch-edouard-toulouse.mssante.fr",
                "ch-aix.mssante.fr",
                "ch-montperrin.mssante.fr",
                "ch-valvert.mssante.fr",
                "ch-arles.mssante.fr",
            ],
        },
        "filename": "ght13.json",
        "name": "ght13",
    },
]


def main(directory):
    logger = logging.getLogger("test")
    re_rpps_fn = re.compile(r".*?(ExtractionMonoTable_CAT18_ToutePopulation_(\d+).csv)")
    _fmt = "%Y%m%d%H%M"

    logger.info("File : {}".format(directory))
    absdir = os.path.abspath(directory)

    data = {}
    for domain in MSSANTE:
        data[domain["name"]] = dict(mssante={})
        for dom in domain["domains"]["value"]:
            data[domain["name"]]["mssante"][dom] = []

    for fn in sorted(os.listdir(absdir)):
        # ExtractionMonoTable_CAT18_ToutePopulation_201805260809.csv

        logger.info("File {}".format(fn))
        filename = os.path.join(absdir, fn)

        if os.path.isfile(filename) and re_rpps_fn.match(fn):
            logger.info("File abs {}".format(filename))

            df = pandas.read_csv(
                filename,
                delimiter=";",
                names=practitioner.RPPS.KEYS_CAT18,
                header=0,
                index_col=False,
            )
            df2 = df.loc[
                df.drop_duplicates("adresse_bal_mssante")
                .adresse_bal_mssante.dropna()
                .index
            ]
            mss_providers = df2.adresse_bal_mssante.str.split("@", expand=True).get(1)

            _date = dt.strptime(re_rpps_fn.match(fn).group(2), _fmt)

            for domain in MSSANTE:
                for dom in domain["domains"]["value"]:
                    _count = mss_providers.where(mss_providers == dom).dropna().count()
                    logger.info("Add {}={} to {}".format(_date, _count, dom))
                    data[domain["name"]]["mssante"][dom].append(
                        dict(date=_date.strftime("%Y-%m-%d"), value=int(_count))
                    )

    for domain in MSSANTE:
        fn = os.path.join(absdir, domain["filename"])
        logger.info("Save {}".format(fn))
        with open(fn, "w") as fout:
            helpers.save_json(fn, data[domain["name"]])


if __name__ == "__main__":
    print(sys.path)

    loggers = helpers.stdout_logger(["diff", "digester", "test"], logging.INFO)
    main(sys.argv[1])
