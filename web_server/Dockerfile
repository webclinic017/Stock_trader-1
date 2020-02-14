#FROM python:3

#ADD requirements.txt /
#RUN pip install -r requirements.txt

#ADD driver_webserver.py /

#CMD ["python", "./driver_webserver.py"]
FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add bash nano
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt