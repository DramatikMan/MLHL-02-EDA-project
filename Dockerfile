FROM python:3.10-slim AS base
SHELL ["/bin/bash", "-c"]
WORKDIR /project
ENV PYTHONPATH "${PYTHONPATH}:/project"
COPY pyproject.toml poetry.lock* ./
COPY scripts scripts
COPY app app

RUN apt update && apt install \
    wget \
    unzip \
    cron \
    -y
RUN wget \
    -q https://chromedriver.storage.googleapis.com/98.0.4758.80/chromedriver_linux64.zip \
    -O temp.zip \
    && unzip temp.zip -d /usr/bin \
    && rm temp.zip
RUN wget \
    -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_98.0.4758.80-1_amd64.deb \
    -O temp.deb \
    && apt install ./temp.deb -y \
    && rm temp.deb

COPY crontab /etc/cron.d/scraper
RUN sed -i "s/PROJECT_DIR/\\${PWD}/g" /etc/cron.d/scraper
RUN chmod 0644 /etc/cron.d/scraper
RUN crontab /etc/cron.d/scraper

FROM base AS development
RUN scripts/poetry_install.sh
CMD scripts/run_jupyter.sh

FROM base AS testing
RUN scripts/poetry_install.sh
CMD poetry exec type_check && poetry exec lint

FROM base AS production
COPY poetry.lock .
ARG build_env
RUN scripts/poetry_install.sh
RUN rm -r scripts
# cron ignores env variables which are stored outside /etc/environment (e.g. variables passed via docker ENV command or -e flag)
CMD printenv > /etc/environment && cron -f