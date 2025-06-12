FROM python:3.12-slim-bullseye
#install uv packge installer
#https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/


RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg dependencies
  && apt-get install -y libpq-dev postgresql-client \
  # gunzip
  && apt-get install -y gzip \
  # Additional dependencies (debigging optional)
  && apt-get install -y git procps telnet \
  # cleaning up unused files \
  # following for nc and debugging -optional
  && apt-get install -y --no-install-recommends gcc netcat curl tmux screen vim  \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*


WORKDIR /

# Copy app code and csv data
COPY imdb/ /app/imdb
COPY .env /app
COPY compose/imdb/entrypoint.sh /entrypoint.sh
COPY compose/imdb/start.sh /start.sh
COPY data /app/data

#remove cr if from windows
RUN sed -i 's/\r$//g' /entrypoint.sh
RUN sed -i 's/\r$//g' /start.sh    #remove cr


COPY ./pyproject.toml /pyproject.toml
COPY ./uv.lock /uv.lock
# Sync the project into a new environment

#https://github.com/astral-sh/uv/issues/8085#issuecomment-2406665798
RUN uv export  | uv pip install -r - --system   # until uv sync --system works again.

RUN chmod +x /entrypoint.sh /start.sh

CMD ["/start.sh"]