FROM alpine:3.13.5

RUN apk --update add python3 bash py-pip

RUN python3 --version

RUN pip3 install --no-cache --upgrade pip
RUN pip3 install --no-cache pytz==2021.1 mako==1.1.4
RUN pip3 install --no-cache twine==2.0
RUN pip3 install --no-cache coverage==5.5
RUN pip3 install --no-cache Sphinx==3.5.4
RUN pip3 install --no-cache sphinx_rtd_theme==0.5.2

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /periodtask

WORKDIR /periodtask
