FROM octue/check-semantic-version:1.0.0.beta-9

COPY . .
RUN pip install -e .

COPY check_semantic_version/entrypoint.sh /entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
