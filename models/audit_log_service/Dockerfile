FROM python:alpine3.7

RUN pip install --upgrade pip

ADD ./ audit_log_service/
WORKDIR audit_log_service
ADD requirements.txt /

RUN pip install -r requirements.txt

ADD logger.py /
ADD logger_api.py /

CMD python ./logger_api.py