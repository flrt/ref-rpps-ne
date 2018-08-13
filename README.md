Informations sur le RPPS
========================

Le projet analyse 

- la nouvelle extraction publique du RPPS, disponible sur le site [annuaire.sante.fr](https://annuaire.sante.fr/web/site-pro/extractions-publiques); 
- la nouvelle extraction publique de la MSSanté, disponible sur le site [annuaire.sante.fr](https://annuaire.sante.fr/web/site-pro/extractions-mss)


Il effectue les actions suivantes (en fonction de la configuration) :

- téléchargement de la version actuelle (zip+extraction)
- calcul de la différence avec la version précédente
- production d'un flux d'informations Atom/RSS avec des données de suivi (générales et plus spécifiques) 

Le flux RSS/Atom est disponible sur la page dédiée [opikanoba.org/feeds](https://www.opikanoba.org/feeds)

La configuration du projet par défaut permet de produire (toujours via configuration)
- des fichiers de différences : un contenant les numéros de lignes ayant changées, un contenant les lignes complètes
- des fichiers json d'informations de données principalement axés sur des statistiques en lien avec les adresses mail [MSSanté](https://www.mssante.fr/)
    - top 10 des domaines MSSAnté
    - suivi du nombre de mail MSSanté par CHU
    - suivi du nombre de mail MSSanté dans des groupements d'établissements (GHT)


Informations techniques:

- génération flux RSS : utilisation du projet [atom_to_rss2](https://github.com/flrt/atom_to_rss2)
- génération flux Atom : utilisation du projet [atom_gen](https://github.com/flrt/atom_gen)
- upload flux RSS + donnees sur FTP : utilisation du projet [atom_gen](https://github.com/flrt/atom_gen)
- utilisation de [pandas](https://pandas.pydata.org) pour l'exploitation des données

# Licence 

[MIT](LICENSE) pour le code

[CC BY-SA 3.0 FR](https://creativecommons.org/licenses/by-sa/3.0/fr/) pour le contenu ATOM