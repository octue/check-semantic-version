FROM --platform=linux/amd64 python:3.10.14-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends curl git jq && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/idc101/git-mkver/releases/download/v1.3.0/git-mkver-linux-x86_64-1.3.0.tar.gz \
    | tar xvz \
    && mv git-mkver /usr/local/bin

ARG VERSION
RUN pip3 install git+https://github.com/octue/check-semantic-version@${VERSION}

COPY check_semantic_version/entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
