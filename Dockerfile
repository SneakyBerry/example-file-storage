FROM python:3.7.4-alpine3.10 as builder

ARG DEVELOPMENT_BUILD=true
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONIOENCODING=utf-8 \
    POETRY_VIRTUALENVS_CREATE="false"

WORKDIR /src

RUN apk add --no-cache gcc make musl-dev libffi-dev libressl-dev git

RUN pip install -U pip==20.2.3 \
    && pip install poetry==1.0.10

ADD pyproject.toml poetry.lock /src/
RUN poetry export \
        --format requirements.txt \
        --output requirements.txt \
        --without-hashes \
        --with-credentials \
        $(test "$DEVELOPMENT_BUILD" = "true" && echo "--dev") \
    && apk add --no-cache postgresql-dev \
    && mkdir /wheels \
    && pip wheel -r requirements.txt --wheel-dir /wheels \
    && rm requirements.txt

FROM python:3.7.4-alpine3.10

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_INDEX=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /src

COPY --from=builder /wheels /wheels
RUN apk add --no-cache libpq libssl1.1 \
 && pip install /wheels/*

COPY . .

ENTRYPOINT ["/bin/sh"]
