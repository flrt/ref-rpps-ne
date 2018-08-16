FROM python:3.6
LABEL maintainer="frederic.laurent@gmail.com"

RUN apt-get update
RUN apt-get -y install python3-lxml
RUN pip install --upgrade pip

# install python package
RUN pip install requests
RUN pip install lxml
RUN pip install html5lib
RUN pip install bs4
RUN pip install mailer
RUN pip install xlrd
RUN pip install arrow
RUN pip install pandas
RUN pip install tweepy

WORKDIR /opt

RUN mkdir /opt/feed
ADD cert /opt/cert/
ADD default /opt/default

ADD *.py /opt/

# install lib to produce Atom/RSS
RUN git clone https://github.com/flrt/atom_gen.git /opt/atom_gen
RUN pip install /opt/atom_gen/dist/atom_gen-1.0.tar.gz
RUN git clone https://github.com/flrt/atom_to_rss2.git atomtorss2

ADD run.sh /opt/run.sh

