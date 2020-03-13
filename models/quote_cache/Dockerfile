FROM python:alpine3.7

RUN pip install --upgrade pip

ADD ./ quote_cache/
WORKDIR quote_cache
ADD requirements.txt /

RUN pip install -r requirements.txt

ADD quote_cache.py /
ADD quote_cache_api.py /

CMD python ./quote_cache_api.py