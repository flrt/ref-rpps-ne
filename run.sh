#!/usr/bin/env bash

export PYTHONPATH=/opt

echo "Run Look out RPPS"
python lookout.py --conf conf/config-rpps.json
#\
#                     --dataftp conf/ftp-data-rpps.json \
#                     --feedftp conf/ftp-feed-rpps.json

echo "Run Look out MSSante"
python lookout.py --conf conf/config-mssante.json
#\
#                     --dataftp conf/ftp-data-mssante.json \
#                     --feedftp conf/ftp-feed-mssante.json