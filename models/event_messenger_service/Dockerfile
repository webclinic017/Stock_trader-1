FROM python:alpine3.7

RUN pip install --upgrade pip

ADD ./ event_messenger_service/
WORKDIR event_messenger_service
ADD requirements.txt /

RUN pip install -r requirements.txt

ADD event_messenger.py /
ADD event_messenger_api.py /

CMD python ./event_messenger_api.py