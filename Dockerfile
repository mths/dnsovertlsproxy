FROM python:3-alpine

USER root

COPY ./ /dnsovertlsproxy

WORKDIR /dnsovertlsproxy

RUN python3 setup.py install

CMD ["dnsovertlsproxy", "--listen_port", "50053"]
