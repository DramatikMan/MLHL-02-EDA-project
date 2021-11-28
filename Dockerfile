FROM python:3.9.7-slim AS base
SHELL ["/bin/bash", "-c"]
WORKDIR /project
ENV PYTHONPATH "${PYTHONPATH}:/project"
RUN apt update && apt install \
    wget \
    unzip \
    cron \
    -y
RUN wget \
    -q https://chromedriver.storage.googleapis.com/95.0.4638.69/chromedriver_linux64.zip \
    -O temp.zip \
    && unzip temp.zip -d /usr/bin \
    && rm temp.zip
RUN wget \
    -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_95.0.4638.69-1_amd64.deb \
    -O temp.deb \
    && apt install ./temp.deb -y \
    && rm temp.deb
COPY pyproject.toml .
COPY scripts scripts
COPY app app

COPY crontab /etc/cron.d/scraper
RUN sed -i "s/PROJECT_DIR/\\${PWD}/g" /etc/cron.d/scraper
RUN chmod 0644 /etc/cron.d/scraper
RUN crontab /etc/cron.d/scraper
# cron ignores env variables which are stored outside /etc/environment (e.g. variables passed via docker ENV command or -e flag)
RUN printenv > /etc/environment

FROM base AS development
CMD bash scripts/poetry_install.sh \
    && bash scripts/run_jupyter.sh

FROM base AS production
COPY poetry.lock .
ARG build_env
RUN bash scripts/poetry_install.sh
RUN rm -r scripts
CMD cron -f