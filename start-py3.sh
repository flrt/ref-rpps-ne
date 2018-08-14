#!/usr/bin/env bash
docker run -t -rm -v "$PWD"/log:/opt/log  \
                  -v "$PWD"/config:/opt/config \
                  -v "$PWD"/files:/opt/files \
                  ref-rpps-ne:latest sh /opt/run.sh
