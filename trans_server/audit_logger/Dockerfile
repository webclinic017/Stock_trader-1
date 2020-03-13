FROM python:alpine3.7

RUN pip install --upgrade pip

ADD ./ audit_logger/
WORKDIR audit_logger
# ADD random_test.py /
ADD AuditCommandType.py /
ADD AuditLogBuilder.py /

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "-u", "AuditLogBuilder.py"]