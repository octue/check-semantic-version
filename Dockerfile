FROM octue/check-semantic-version:1.0.0.beta-9

RUN curl -L https://github.com/idc101/git-mkver/releases/download/v1.3.0/git-mkver-linux-x86_64-1.3.0.tar.gz \
    | tar xvz \
    && mv git-mkver /usr/local/bin

COPY . .
RUN pip install -e .

COPY check_semantic_version/entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
