FROM alpine:3.6

RUN apk --update add python3

STOPSIGNAL SIGINT
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /periodtask