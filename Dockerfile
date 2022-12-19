FROM python:3.10.7-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl git && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/idc101/git-mkver/releases/download/v1.2.1/git-mkver-linux-amd64-1.2.1.tar.gz \
    | tar xvz \
    && mv git-mkver /usr/local/bin

RUN pip3 install git+https://github.com/octue/check-semantic-version@1.0.0.beta-5

COPY check_semantic_version/entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
