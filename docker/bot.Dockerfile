FROM python:latest
MAINTAINER Mark Watson <markwatsonatx@gmail.com>
RUN mkdir -p /usr/src/bot
COPY requirements.txt /usr/src/bot/requirements.txt
COPY run.py /usr/src/bot/run.py
COPY souschef /usr/src/bot/souschef
WORKDIR /usr/src/bot
RUN pip install -r requirements.txt
CMD ["python","run.py"]