########################################
#              BUILD IMAGE             #
########################################

FROM python:3.7-slim-buster

ENV POETRY_VERSION=1.1.4 \
    VENV_PATH=/opt/venv \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

ENV PATH=$VENV_PATH/bin:$PATH
WORKDIR /app


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        git \
        default-libmysqlclient-dev \
        libxmlsec1 \
        libxmlsec1-dev \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv $VENV_PATH \
    && pip install poetry==$POETRY_VERSION \
    && poetry config virtualenvs.create false 


COPY poetry.lock pyproject.toml ./

RUN poetry install

COPY . /app

ENTRYPOINT ["/app/docker-entrypoint.sh"]
