FROM alpine:3.6

RUN apk --update add python3 bash

RUN pip3 install --no-cache --upgrade pip
RUN pip3 install --no-cache pytz==2018.5 mako==1.0.7
RUN pip3 install --no-cache twine==1.11.0
RUN pip3 install --no-cache coverage==4.5.1
RUN pip3 install --no-cache Sphinx==1.7.5
RUN pip3 install --no-cache sphinx_rtd_theme==0.4.0

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /periodtask

WORKDIR /periodtask
