FROM alpine:3.6

RUN apk --update add python3 bash

RUN pip3 install --no-cache pytz==2017.2 mako==1.0.7

STOPSIGNAL SIGINT
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /periodtask
