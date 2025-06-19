# BUILDER IMAGE
FROM artifactory.cnes.fr/hysope2-docker/hys2/python-slim:3.8-slim as build
USER 0

WORKDIR /app
# copy necessary files
COPY pyproject.toml ./
COPY py_hydroweb/ py_hydroweb/

# install temporary required packages
RUN --mount=type=secret,id=secret \
    --mount=type=cache,target=/var/cache/buildkit/pip \
    set -eux ; \
    [ -e /run/secrets/secret ] && . /run/secrets/secret ; \
    [ -e /kaniko/run/secrets/secret ] && . /kaniko/run/secrets/secret ; \
    pip install --upgrade pip ; \
    pip install --no-cache-dir . ;

USER user


# TEST IMAGE
FROM build as test

ENV PIP_CACHE_DIR=/var/cache/buildkit/pip

USER 0

# copy necessary files
WORKDIR /app
COPY tests ./tests
COPY setup.cfg setup.cfg

# install make and tests deps
RUN --mount=type=secret,id=secret \
    --mount=type=cache,target=/var/cache/buildkit/pip \
    set -eux ; \
    [ -e /run/secrets/secret ] && . /run/secrets/secret ; \
    [ -e /kaniko/run/secrets/secret ] && . /kaniko/run/secrets/secret ; \
    apt-get update ; \
    apt-get install --no-install-recommends -y make ; \
    pip install --upgrade pip ; \
    pip install .[dev] ;

COPY --from=artifactory.cnes.fr/hysope2-docker/hys2/dockerfile-custom-stages:latest python-ci-env-stage/Makefile Makefile

ENTRYPOINT []


# DEV CONTAINER IMAGE
FROM test as dev

ENV MODULES_DIRECTORIES="py_hydroweb"

USER 0

COPY --from=artifactory.cnes.fr/hysope2-docker/hys2/dockerfile-custom-stages:latest python-dev-env-stage/ /tmp/

RUN --mount=type=secret,id=secret \
    --mount=type=cache,target=/var/cache/apt \
    set -eux ; \
    [ -e /run/secrets/secret ] && . /run/secrets/secret ; \
    [ -e /kaniko/run/secrets/secret ] && . /kaniko/run/secrets/secret ; \
    /tmp/install-script.sh ;

USER user

ENTRYPOINT [ "/docker-entrypoint.sh" ]

CMD ["bash"]

# ----------------------------
# IMAGE PUBLICATION (Define and copy files for publication)
FROM artifactory.cnes.fr/hysope2-docker/hys2/python-slim:3.8-slim-publier AS publication

USER 0

ARG TWINE_REPOSITORY_URL
ARG TWINE_CERT=/etc/ssl/certs/ca-certificates.trust.crt

COPY py_hydroweb/ py_hydroweb/
COPY pyproject.toml pyproject.toml
COPY README.md README.md