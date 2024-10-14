FROM octue/check-semantic-version:1.0.0.beta-9

# Install poetry.
ENV POETRY_HOME=/root/.poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - && poetry config virtualenvs.create false;

COPY . .
RUN poetry install

COPY check_semantic_version/entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
