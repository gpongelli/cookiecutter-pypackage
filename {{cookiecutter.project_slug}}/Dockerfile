# ref.  https://github.com/jmaupetit/md2pdf

# -- Base image --
FROM python:3.12-slim as base

ARG IMAGE_TIMESTAMP
ARG IMAGE_AUTHORS
ARG PKG_VERSION
ARG IMAGE_LICENSE
ARG IMAGE_DOC
ARG IMAGE_SRC
ARG IMAGE_URL
ARG IMAGE_GIT_HASH
ARG IMAGE_DESCRIPTION

# https://snyk.io/blog/how-and-when-to-use-docker-labels-oci-container-annotations/
# https://github.com/opencontainers/image-spec/blob/main/annotations.md#pre-defined-annotation-keys
LABEL org.opencontainers.image.created="${IMAGE_TIMESTAMP}"
LABEL org.opencontainers.image.authors="${IMAGE_AUTHORS}"
LABEL org.opencontainers.image.version="${PKG_VERSION}"
LABEL org.opencontainers.image.licenses="${IMAGE_LICENSE}"
LABEL org.opencontainers.image.documentation="${IMAGE_DOC}"
LABEL org.opencontainers.image.source="${IMAGE_SRC}"
LABEL org.opencontainers.image.url="${IMAGE_URL}"
LABEL org.opencontainers.image.revision="${IMAGE_GIT_HASH}"
LABEL org.opencontainers.image.description="${IMAGE_DESCRIPTION}"

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
