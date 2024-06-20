# ref.  https://github.com/jmaupetit/md2pdf

# -- Base image --
FROM python:3.12-slim as base

LABEL org.opencontainers.image.authors="{{ cookiecutter.email }}"

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade pip

# Upgrade system packages to install security updates
RUN apt update && \
    apt -y upgrade
    # && \
    # apt -y install g++ gcc
    # g++ and gcc needed by pytomlpp

# -- Builder --
FROM base as builder

WORKDIR /build

COPY . /build/

ENV PATH  $PATH:/root/.local/bin

# Install poetry
RUN pip install pipx && \
    pipx install poetry

ARG PKG_VERSION

# Build and install package
RUN poetry build && \
    pip install dist/*-$PKG_VERSION-*.whl

# -- Core --
FROM base as core

COPY --from=builder /usr/local /usr/local

# -- App --
FROM core as production

VOLUME ["/app"]

WORKDIR /app

USER "1000:1000"

ENTRYPOINT ["{{ cookiecutter.project_slug }}"]
