FROM python:2.7-buster

EXPOSE 55271

RUN mkdir -p /app/src && mkdir -p /app/requirements
COPY requirements /app/requirements
COPY requirements_postgre.txt /app/requirements_postgre.txt

RUN apt-get update && apt-get install -y uwsgi uwsgi-plugin-python && rm -rf /var/lib/apt/lists/*
RUN pip install -r /app/requirements_postgre.txt
RUN ln -s /usr/lib/python2.7/plat-x86_64-linux-gnu/_sysconfigdata_nd.py /usr/lib/python2.7

COPY docker-build/uwsgi.ini /app
COPY src /app/src

RUN useradd -m -d /app --uid 1000 app && chown -R app /app
USER app
WORKDIR "/app"

VOLUME "/app/settings"

ENTRYPOINT ["/usr/bin/uwsgi", "--ini", "/app/uwsgi.ini"]
