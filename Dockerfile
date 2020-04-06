FROM c0defox/alpine-pylint:latest
ADD ./src /opt
WORKDIR /opt
ENTRYPOINT ["pylint_runner"]
