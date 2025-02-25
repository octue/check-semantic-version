# Use the last known working image for this repo as the base to get around the unknown changes in system dependencies
# stopping `octue/check-semantic-version` from running as a GitHub action. The drawback to this is we can't easily
# update `git-mkver` as newer versions require changes in the system dependencies.
FROM octue/check-semantic-version:1.0.0.beta-9

# Install poetry.
ENV POETRY_HOME=/root/.poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - && poetry config virtualenvs.create false;

COPY . .
RUN poetry install

ENTRYPOINT ["check-semantic-version"]
