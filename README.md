Informations sur le RPPS
========================

Le projet analyse 

- la nouvelle extraction publique du RPPS, disponible sur le site [annuaire.sante.fr](https://annuaire.sante.fr/web/site-pro/extractions-publiques); 
- la nouvelle extraction publique de la MSSanté, disponible sur le site [annuaire.sante.fr](https://annuaire.sante.fr/web/site-pro/extractions-mss)


Il effectue les actions suivantes (en fonction de la configuration) :

- téléchargement de la version actuelle (zip+extraction)
- calcul de la différence avec la version précédente
- production d'un flux d'informations Atom/RSS avec des données de suivi (générales et plus spécifiques) 
- production pour chaque fichier, de fichiers résultant de l'analyse

Deux fichiers RSS2 et Atom sont disponibles sur la page dédiée [opikanoba.org/feeds](https://www.opikanoba.org/feeds),
permettant de voir ce qui est produit.

## Structure du projet
### Structure minimale
Pour démarrer aucun fichier n'est nécessaire. Voir la commande avec docker.
La structure est la suivante :

- repertoire `log` : logs
- repertoire `conf` : la configuration
- repertoire `files` : les fichiers telechargés et de travail (sha des fichiers, fichiers index, fichiers diff)

### Structure complète
La structure est la suivante :

- répertoire `cert` : fichiers contenant les fichiers permettant de faire les requetes https
- repertoire `log` : logs
- répertoire `default` : fichiers de configuration par défaut
- repertoire `conf` : la configuration
- répertoire `feed` : contient les fichiers RSS2 et Atom produits
- repertoire `files` : les fichiers telechargés et de travail (sha des fichiers, fichiers index, fichiers diff)
- répertoire `test` : tests
- à la racine les fichiers *.py


## Configuration

La configuration du projet par défaut permet de produire :

- des fichiers de différences : un contenant les numéros de lignes ayant changées (`index_<nom fichier original>`), 
un contenant les lignes complètes (`new_<nom fichier original>`)
- des fichiers `json d'informations de données principalement axés sur des statistiques en lien avec les 
adresses mail [MSSanté](https://www.mssante.fr/) :

    - top 10 des domaines MSSanté
    - suivi du nombre de mail MSSanté par CHU
    - suivi du nombre de mail MSSanté dans des groupements d'établissements (GHT)

### Configuration RPPS
Le fichier de configuration `config-rpps.json est pris en compte dans le répertoire conf. S'il est absent,
le programme en initialise un. Il contient :

- des informations sur la date du dernier fichier analysé
- des données de configuration locale
- l'URL de publication des fichiers RSS/Atom
- des données de configuration sur les données à suivre

### Configuration MSSanté
Le même principe est appliqué que sur `config-rpps.json` est appliqué sur `config-mssante.json`.

### Configuration d'upload des données
Le fichier de configuration ftp-data.json` permet d'uploader par FTP sur un site distant les données produites. 
Les fichiers pouvant être uploadé :

- fichier d'index des nouveautés : fichiers `index_*.txt`
- fichier des différences contenant les données : fichiers `new_*.txt`
- fichiers de suivi : `*.json

Si le fichier de configuration n'est pas présent dans le répertoire conf, les fichiers restent en local.

Le fichier de configuration `ftp-feed.json permet d'uploader par FTP les fichiers RSS2 et Atom produits. Si le 
fichier n'est pas présent dans le répertoire conf, aucune action d'upload n'est faite.


## Exécution sans docker
Après avoir cloner le projet, le fichier `run.sh` contient les commandes de lancement de l'analyse RPPS et MSSanté.

Un simple 
     
    sh run.sh 
    
Pour paramétrer le lancement et connaitre les paramètres :


    $ python3.6 lookout.py
    /!\ Aucune action définie !

    usage: lookout.py [-h] [--config CONFIG] [--feedftp FEEDFTP]
                  [--dataftp DATAFTP] [--zip ZIP] [--txt TXT] [--stat STAT]

    optional arguments:
      -h, --help         show this help message and exit
      --config CONFIG    fichier de parametres
      --feedftp FEEDFTP  configuration FTP pour upload du flux ATOM, format JSON
      --dataftp DATAFTP  configuration FTP pour upload des données, format JSON
      --zip ZIP          Fichier ZIP contenant l'extraction RPPS ou MSSante
      --txt TXT          Fichier texte contenant l'extraction RPPS ou MSSante
                         (pour stats)
     --stat STAT        Affiche les stats
     
## Execution avec docker
Le conteneur est nommé ref-rpps-ne dans [docker hub](https://hub.docker.com/r/flrt/ref-rpps-ne/).
Pour lancer l'analyse, il suffit de créer un répertoire d'accueil des fichiers produits :

    mkdir rpps-mssante
    cd rpps-mssante

et de lancer 

    docker run -t --rm -v "$PWD"/log:/opt/log  \
                -v "$PWD"/conf:/opt/conf \
                -v "$PWD"/files:/opt/files \
                ref-rpps-ne sh run.sh

Cette commande permet de lancer l'analyse des fichiers RPPS et MSSanté en utilisant les 
répertoires locaux dans lesquels seront stockés :


La commande peut être lancée sans aucune donnée de configuration. Les données de configuration peuvent être changées 
par la suite pour être prises en compte.


# Informations techniques:

- génération flux RSS : utilisation du projet [atom_to_rss2](https://github.com/flrt/atom_to_rss2)
- génération flux Atom : utilisation du projet [atom_gen](https://github.com/flrt/atom_gen)
- upload flux RSS + donnees sur FTP : utilisation du projet [atom_gen](https://github.com/flrt/atom_gen)
- utilisation de [pandas](https://pandas.pydata.org) pour l'exploitation des données


# Licence 

[MIT](LICENSE) pour le code

[CC BY-SA 3.0 FR](https://creativecommons.org/licenses/by-sa/3.0/fr/) pour le contenu ATOM