FROM octue/check-semantic-version:1.0.0.beta-9

RUN apt-get update && apt-get install -y --no-install-recommends curl git jq && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/idc101/git-mkver/releases/download/v1.3.0/git-mkver-linux-x86_64-1.3.0.tar.gz \
    | tar xvz \
    && mv git-mkver /usr/local/bin

# Install poetry.
ENV POETRY_HOME=/root/.poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - && poetry config virtualenvs.create false;

COPY . .
RUN poetry install

COPY check_semantic_version/entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
