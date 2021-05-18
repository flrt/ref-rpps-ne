#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Analyze RPPS file

"""
__author__ = "Frederic Laurent"
__version__ = "1.0"
__copyright__ = "Copyright 2017, Frederic Laurent"
__license__ = "MIT"


import logging
import os.path
import pprint
import re
import tempfile
import zipfile
from collections import OrderedDict
from datetime import datetime as dt

import pandas
import requests

from easy_atom import helpers


class RPPS:
    """
        Handle RPPS Data
    """

    PEM = "cert/asiproot.pem"
    KEYS_PERS_ACT = [
        "type_identifiant_pp",
        "identifiant_pp",
        "identification_nationale_pp",
        "code_civilite_exercice",
        "libelle_civilite_exercice",
        "code_civilite",
        "libelle_civilite",
        "nom_exercice",
        "prenom_exercice",
        "code_profession",
        "libelle_profession",
        "code_categorie_professionnelle",
        "libelle_categorie_professionnelle",
        "code_type_savoir_faire",
        "libelle_type_savoir_faire",
        "code_savoir_faire",
        "libelle_savoir_faire",
        "code_mode_exercice",
        "libelle_mode_exercice",
        "numero_siret_site",
        "numero_siren_site",
        "numero_finess_site",
        "numero_finess_etablissement_juridique",
        "identifiant_technique_structure",
        "raison_sociale_site",
        "enseigne_commerciale_site",
        "complement_destinataire",
        "complement_point_geographique",
        "numero_voie",
        "indice_repetition_voie",
        "code_type_de_voie",
        "libelle_type_de_voie",
        "libelle_voie",
        "mention_distribution",
        "bureau_cedex",
        "code_postal",
        "code_commune",
        "libelle_commune",
        "code_pays",
        "libelle_pays",
        "telephone",
        "telephone_2",
        "telecopie",
        "adresse_e-mail",
        "code_departement",
        "libelle_departement",
        "ancien_identifiant_structure",
        "autorit_enregistrement",
    ]
    KEYS_SAV_FAIRE = [
        "type_identifiant_pp",
        "identifiant_pp",
        "identification_nationale_pp",
        "nom_exercice",
        "prenom_exercice",
        "code_profession",
        "libelle_profession",
        "code_cat_prof",
        "libelle_cat_prof",
        "code_type_savoir_faire",
        "libelle_type_savoir_faire",
        "code_savoir_faire",
        "libelle_savoir_faire",
    ]
    KEYS_DIPLOME = [
        "type_identifiant_pp",
        "identifiant_pp",
        "identification_nationale_pp",
        "nom_exercice",
        "prenom_exercice",
        "code_type_diplome",
        "libelle_type_diplome",
        "code_diplome",
        "libelle_diplome",
        "code_type_autorisation",
        "libelle_type_autorisation",
        "code_discipline_autorisation",
        "libelle_discipline_autorisation",
    ]
    KEYS_MSSANTE = [
        "type_bal",
        "adresse_bal",
        "type_identifiant_pp",
        "identifiant_pp",
        "identification_nationale_pp",
        "type_identifiant_structure",
        "identification_structure",
        "service_rattachement",
        "civilite_exercice",
        "nom_exercice",
        "prenom_exercice",
        "cat_profession",
        "libelle_cat_profession",
        "code_profession",
        "libelle_profession",
        "code_savoir_faire",
        "libelle_savoir_faire",
        "dematerialisation",
        "raison_sociale_structure_bal",
        "enseigne_commerciale_structure_bal",
        "complement_localisation_structure_bal",
        "complement_distribution_structure_bal",
        "numero_voie_structure_bal",
        "complement_numero_voie_structure_bal",
        "type_voie_structure_bal",
        "libelle_voie_structure_bal",
        "lieudit_mention_structure_bal",
        "ligne_acheminement_structure_bal",
        "code_postal_structure_bal",
        "departement_structure_bal",
        "pays_structure_bal",
    ]

    MAPPING = {
        "PS_LibreAcces_Dipl_AutExerc": KEYS_DIPLOME,
        "PS_LibreAcces_Personne_activite": KEYS_PERS_ACT,
        "PS_LibreAcces_SavoirFaire": KEYS_SAV_FAIRE,
        "Extraction_Correspondance_MSSante": KEYS_MSSANTE,
    }

    def __init__(self, properties):
        self.logger = logging.getLogger("downloader")
        self.local_storage = tempfile.gettempdir()
        self.tracks = {}
        self.data_url = ""
        self.data_files = []
        self.last_check_date = None
        self.re_rpps_fn = re.compile(".*?(PS_LibreAcces_Personne_activite_(\d+).(txt))")
        self.re_enddate = re.compile("(.*?)_(\d{12})\.(txt|zip)")
        self.data_date = dt.now().strftime("%Y-%m-%d")
        self.init_properties(properties)

    def init_properties(self, properties):
        """
            properties bootstrap

        :param properties: properties object
        :return: -
        """
        try:
            self.data_url = properties.URL
        except AttributeError as ae:
            self.logger.warning(f"[config] No/Wrong URL properties : {ae}")

        try:
            self.last_check_date = properties.local.last_check
        except AttributeError as ae:
            self.logger.warning(f"[config] No/Wrong local.last_check properties : {ae}")

        try:
            self.local_storage = properties.local.storage
        except AttributeError as ae:
            self.logger.warning(f"[config] No/Wrong local.storage properties : {ae}")
            self.logger.info(f"Using temp dir : {self.local_storage}")

        try:
            self.tracks = properties.tracks
        except AttributeError as ae:
            self.logger.warning(f"[config] No/Wrong tracks properties : {ae}")

    def find_current_data(self):
        """
            Find the current remote filename

            Make an HEAD request to grab information

            HTTPS web site. cert are stored in RPPS.PEM

        :return:
            remote_fn : remote zip filename
        """
        pem_filename = os.path.abspath(RPPS.PEM)
        req = requests.head(self.data_url, verify=pem_filename)

        _filename = None

        if req.status_code == 200:
            # Content-Disposition': 'attachment; filename=PS_LibreAcces_201808011050.zip'
            regex_filename = re.match(
                ".*?filename=(.*)", req.headers["Content-Disposition"]
            )
            if regex_filename:
                _filename = regex_filename.group(1)
        else:
            self.logger.warning(f"Error accessing URL [{req.status_code}] {self.data_url}")

        return _filename

    def root_data_filename(self, url):
        re_eval = self.re_enddate.match(url)
        if re_eval:
            return re_eval.group(1)
        else:
            return ""

    def extract_data_filename(self, url):
        """
            Extract data, given the URL
            blabla/PS_LibreAcces_Personne_activite_201807300827.txt

        :param url: URL of the file
        :return:
            remote file name
            data date (ex: 201807300827)
        """
        self.logger.debug(f"Extract data from {url}")
        re_eval = self.re_enddate.match(url)
        if re_eval:
            remote_fn = re_eval.group(0)
            data_date = re_eval.group(2)
            return remote_fn, data_date

        return None, None

    def parse_date(self, datestr, fmt="%Y%m%d%H%M"):
        return dt.strptime(datestr, fmt)

    def set_data_date(self, mydate, fmt="%Y-%m-%d"):
        self.data_date = mydate.strftime(fmt)

    def is_newer(self, filename):
        """
            Test if file is newer than the last check
            Last check can be null
        :param filename: new filename (containing date) to compare
        :return: True if the file is newer
        """
        self.logger.debug(f"prev date = {self.last_check_date}")
        if not self.last_check_date:
            return True

        _remote_fn, _date = self.extract_data_filename(filename)
        self.logger.debug(f"extract date from {_remote_fn} -> {_date}")

        delta = self.parse_date(_date) - self.parse_date(self.last_check_date)
        return delta.total_seconds() > 0

    def update_last_check_date(self, filename):
        f, d = self.extract_data_filename(os.path.basename(filename))
        self.last_check_date = d

    def retrieve_current(self):
        _remote_fn = self.find_current_data()
        self.logger.debug(f"Remote={_remote_fn}")

        self.logger.debug(f"prev date = {self.last_check_date}")

        if self.is_newer(_remote_fn):
            self.logger.info("Newer file available -> download")
            # download zip
            return self.download_zip(self.local_storage, _remote_fn)
        return None

    def unzip(self, zfile, dest_dir):
        """
            Unzip file into destination directory
        """
        zipf = zipfile.ZipFile(zfile)
        testzip = zipf.testzip()
        if testzip:
            self.logger.error(f"Zip ERROR : {testzip}")
            return []
        else:
            zipf.extractall(dest_dir)

        return list(map(lambda x: os.path.join(dest_dir, x), zipf.namelist()))

    def download_zip(self, download_dir, remote_zip):
        """
            Download data file (zip format)
            Extract data into storage directory

        :param download_dir: storage directory
        :param remote_zip: remote zip filename
        :return: absolute name of CSV file
        """
        self.logger.info(f"Download zip: {remote_zip}")
        self.logger.info(f"Extract to : {download_dir}")

        if download_dir and not os.path.exists(download_dir):
            os.makedirs(download_dir)

        _filename = os.path.join(download_dir, remote_zip)

        response = requests.get(
            self.data_url, stream=True, verify=os.path.abspath(RPPS.PEM)
        )
        handle = open(_filename, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)
        handle.close()

        return _filename

    def save_diff_files(self, data_filename, diff_filename, difflist):
        """
            Save files

        :param data_filename: file containing hash, line number, values
        :param diff_filename: file containing line numbers of modified data
        :param difflist: list of differences
        :return: -
        """
        self.logger.info(f"Save diff zip files : data={data_filename}, diff={diff_filename}")

        if data_filename:
            with open(data_filename, "w") as fdata:
                for _hash, num, data in difflist:
                    fdata.write(f"{data}\n")

            self.data_files.append(data_filename)

        if diff_filename:
            # save indexes
            with open(diff_filename, "w") as findex:
                index_list = list(map(lambda d: str(d[1]), difflist))
                findex.write("{}\n".format(",".join(index_list)))

            self.data_files.append(diff_filename)

    def extract_data(self, data_filename, difflist):
        """
            Read raws data file
            Produce data according to config in tracks section
                - title
                - list of ordered key:value wih date
            For each block
                - produce RSS section if configured
                - produce json raw data if filename is provided

        :param data_filename:
        :param difflist: list of difference

        :return:
        """

        # category
        cat = self.root_data_filename(os.path.basename(data_filename))
        self.logger.info(f"RPPS Cat={cat}")

        # Read data
        df = pandas.read_csv(
            data_filename,
            delimiter="|",
            names=RPPS.MAPPING[cat],
            header=0,
            index_col=False,
        )

        infos = None
        if cat == "PS_LibreAcces_Dipl_AutExerc":
            infos = [self.PS_LibreAcces_Dipl_AutExerc_Extract(df, difflist)]
        elif cat == "PS_LibreAcces_Personne_activite":
            infos = [self.PS_LibreAcces_Personne_activite_Extract(df, difflist)]
        elif cat == "PS_LibreAcces_SavoirFaire":
            infos = [self.PS_LibreAcces_SavoirFaire_Extract(df, difflist)]
        elif cat == "Extraction_Correspondance_MSSante":
            infos = self.Extraction_Correspondance_MSSante_Extract(df, difflist)
        else:
            pass

        return infos

    def PS_LibreAcces_Dipl_AutExerc_Extract(self, df, difflist):
        return {
            "title": "Informations fichier des Diplômes",
            "type": "stats",
            "values": [
                {"key": "Nombre de lignes", "val": len(df)},
                {"key": "Nombre de lignes modifiées", "val": len(difflist)},
                {"key": "Nombre de RPPS", "val": df.identifiant_pp.nunique()},
                {
                    "key": "Nombre de diplomes differents",
                    "val": df.code_diplome.nunique(),
                },
            ],
            "rss": True,
        }

    def PS_LibreAcces_Personne_activite_Extract(self, df, difflist):
        id_types = df.type_identifiant_pp.value_counts().to_dict()

        infos = {
            "title": "Informations fichier des personnes",
            "type": "stats",
            "values": [
                {"key": "Nombre de lignes", "val": len(df)},
                {"key": "Nombre de lignes modifiées", "val": len(difflist)},
                {"key": "Nombre de RPPS", "val": id_types[8]},
                {"key": "Nombre de ADELI", "val": id_types[0]},
                {
                    "key": "Nombre de Structures référencées",
                    "val": df.identifiant_technique_structure.nunique(),
                },
            ],
            "rss": True,
            "output": None,
            "history_flag": False,
        }
        if "filename" in self.tracks.PS_LibreAcces_Personne_activite._fields:
            infos["output"] = self.tracks.PS_LibreAcces_Personne_activite.filename
        if "save_history" in self.tracks.PS_LibreAcces_Personne_activite._fields:
            infos[
                "history_flag"
            ] = self.tracks.PS_LibreAcces_Personne_activite.save_history
        return infos

    def PS_LibreAcces_SavoirFaire_Extract(self, df, difflist):
        return {
            "title": "Informations fichier des savoir-faire",
            "type": "stats",
            "values": [
                {"key": "Nombre de lignes", "val": len(df)},
                {"key": "Nombre de lignes modifiées", "val": len(difflist)},
                {"key": "Nombre de profession", "val": df.code_profession.nunique()},
            ],
            "rss": True,
        }

    def Extraction_Correspondance_MSSante_Extract(self, df, difflist):

        df.libelle_profession.nunique()
        # top 5 profession
        od = df.libelle_profession.value_counts().head().to_dict(OrderedDict)
        top5_profession = ", ".join([f"{k} ({v})" for k, v in od.items()])

        # bal type
        dd = df.type_bal.value_counts().to_dict(OrderedDict)
        bal_type = ", ".join([f"{k} ({v})" for k, v in od.items()])

        df2 = df.loc[df.drop_duplicates("adresse_bal").adresse_bal.dropna().index]
        mss_providers = df2.adresse_bal.str.split("@", expand=True).get(1)

        general = {
            "title": "Informations MSSanté",
            "type": "stats",
            "values": [
                {"key": "Nombre de lignes", "val": len(df)},
                {"key": "Nombre de lignes modifiées", "val": len(difflist)},
                {
                    "key": "Nombre de profession",
                    "val": f"{df.libelle_profession.nunique()} - top 5 : {top5_profession}",
                },
                {"key": "Mails MSsante", "val": df.adresse_bal.nunique()},
                {"key": "Domaines MSsante", "val": mss_providers.nunique()},
                {"key": "Types de boites aux lettre", "val": bal_type},
            ],
            "rss": True,
        }

        # search if a filename is defined for general infos : stats=true
        for block in self.tracks.Extraction_Correspondance_MSSante:
            if "stats" in block._fields and block.stats:
                general["output"] = block.filename
                general["history_flag"] = (
                    "save_history" in block._fields and block.save_history
                )

        extracted = [general]

        for block in self.tracks.Extraction_Correspondance_MSSante:
            self.logger.info(f"Block {block.name}")

            result = {
                "title": block.name,
                "type": "mssante",
                "values": [],
                "date": self.data_date,
                "rss": "rss" in block._fields and block.rss,
                "history_flag": "save_history" in block._fields and block.save_history,
                "output": None,
            }

            if "top" in block._fields:
                # generate TOP x
                mss_top = (
                    mss_providers.value_counts().head(block.top).to_dict(OrderedDict)
                )
                for (k, v) in mss_top.items():
                    result["values"].append(dict(key=k, val=v))

            if "domains" in block._fields:
                # generate domain section
                if "title" in block.domains:
                    result["title"] = block.domains.title

                for domain in block.domains.value:
                    _count = (
                        mss_providers.where(mss_providers == domain).dropna().count()
                    )
                    result["values"].append(dict(key=domain, val=int(_count)))

            if "filename" in block._fields:
                result["output"] = block.filename
            extracted.append(result)
        return extracted

    def save_tracks(self, data_tracks):
        """
            Save data in filename, if a filename is configured
        :param data_tracks: data to save
        :return saved : name list of data files 
        """
        self.logger.info(f"Save {len(data_tracks)} data tracks")
        pp = pprint.PrettyPrinter(indent=2)
        self.logger.debug(pprint.pformat(data_tracks))

        saved = []

        for data in data_tracks["tracks"]:
            # Save data if needed
            if "output" in data and data["output"]:
                filename = os.path.join(self.local_storage, data["output"])
                self.save_tracks_set(filename, data, data_tracks["date"])
                saved.append(filename)

        return saved

    def save_tracks_set(self, filename, data, date):
        """
            Save data set in filename

        :param filename: filename of the data
        :param data: data to save
        :param date: date of the data
        :param history_flag: handle history or not. History means a list of data sets
        :return: -
        """
        self.logger.info(f"Save tracks set : type={data['type']}, file={filename}")
        pp = pprint.PrettyPrinter(indent=2)
        self.logger.debug(pprint.pformat(data))

        tracks = helpers.load_json(filename)

        if "type" not in data:
            self.logger.warning("No data TYPE, nothing saved...")
            return

        # dtype = data type, e.g. stats, mssante, etc.
        dtype = data["type"]

        if dtype not in tracks:
            # create new set
            tracks[dtype] = {}

        for val in data["values"]:
            if val["key"] not in tracks[dtype]:
                tracks[dtype][val["key"]] = None

            # value to add or remplace (v)
            v = dict(date=date, value=val["val"])

            if data["history_flag"]:
                # Manage a list of values : value = {'date': '2018-03-23', 'value': 999}
                # insert/set/remplace the new value v
                if isinstance(tracks[dtype][val["key"]], list):
                    # already a list
                    # search if these date already exists. If so remplace, else add
                    existing_index = -1
                    for index, elem in enumerate(tracks[dtype][val["key"]]):
                        if elem["date"] == v["date"]:
                            existing_index = index

                    if existing_index > -1:
                        tracks[dtype][val["key"]][existing_index]["value"] = v["value"]
                    else:
                        tracks[dtype][val["key"]].append(v)
                else:
                    # new list (replace single structure)
                    tracks[dtype][val["key"]] = [v]
            else:
                # replace values
                tracks[dtype][val["key"]] = v

        helpers.save_json(filename, tracks)
