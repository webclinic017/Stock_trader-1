FROM python:alpine3.7

RUN pip install --upgrade pip

ADD ./ user_model/
WORKDIR user_model
ADD requirements.txt /

RUN pip install -r requirements.txt

ADD user.py /
ADD user_api.py /
ADD user_tests.py /

CMD python ./user_api.py