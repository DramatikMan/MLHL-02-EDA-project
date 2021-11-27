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

FROM base AS development
CMD rm -rf .venv/* \
    && bash scripts/poetry_install.sh \
    && bash scripts/run_jupyter.sh

FROM base AS production
COPY poetry.lock .
ARG build_env
RUN bash scripts/poetry_install.sh
RUN rm -r scripts
RUN echo "0 5 * * * root cd ${PWD} && poetry run python ${PWD}/app/runner.py &> runner.log; poetry run python ${PWD}/app/notify.py \$?" >> /etc/crontab
RUN crontab /etc/crontab
CMD cron -f