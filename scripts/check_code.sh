#!/bin/bash

clear

poetry run mypy \
    ${PWD}/app \
    --ignore-missing-imports \
    --show-error-codes \
    --strict \
    --exclude /migrations/

poetry run flake8 \
    ${PWD}/app \
    --count \
    --statistics \
    --show-source \
    --exclude /**/migrations