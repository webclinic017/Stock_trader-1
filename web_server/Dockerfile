#FROM ubuntu:16.04

#RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && \
#    apt-get update && apt-get install -y python3.6 python3.6-dev python3-pip

#RUN ln -sfn /usr/bin/python3.6 /usr/bin/python3 && ln -sfn /usr/bin/python3 /usr/bin/python && ln -sfn /usr/bin/pip3 /usr/bin/pip
FROM python:alpine3.7

RUN pip install --upgrade pip

ADD ./ web_server/
WORKDIR web_server
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD driver_webserver.py /
ADD app /

CMD python ./driver_webserver.py