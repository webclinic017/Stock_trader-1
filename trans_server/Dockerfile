#FROM ubuntu:16.04

#RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && \
#    apt-get update && apt-get install -y python3.6 python3.6-dev python3-pip

#RUN ln -sfn /usr/bin/python3.6 /usr/bin/python3 && ln -sfn /usr/bin/python3 /usr/bin/python && ln -sfn /usr/bin/pip3 /usr/bin/pip

FROM python:alpine3.7

RUN pip install --upgrade pip

ADD ./ trans_server/
WORKDIR trans_server
# ADD random_test.py /
ADD audit_logger /
ADD driver_transserver.py /
ADD transaction_server.py /
ADD client.py /
ADD client_data.py /
ADD commands.txt /
ADD currency.py /
ADD event_server.py /
ADD random_test.py /
ADD test_currency.py /

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

# 0 for stubing out the quote seerver
#CMD ["python", "random_test.py"]
#CMD ["python", "transaction_server.py"]
CMD ["python3", "-u", "driver_transserver.py", "--QuoteServer", "0"]