# syntax=docker/dockerfile:1.4
ARG PYTHON_VERSION=3.9
##################
### base image ###
##################
FROM python:${PYTHON_VERSION}-slim AS python-base

# set working directory and env
ARG APPDIR=/usr/src
ARG APPNAME=InvokeAI
WORKDIR ${APPDIR}
ENV PATH=${APPDIR}/${APPNAME}/bin:$PATH

# prepare buildkit cache
ENV PIP_CACHE_DIR=/var/cache/buildkit/pip
RUN \
  mkdir -p ${PIP_CACHE_DIR} \
  && rm -f /etc/apt/apt.conf.d/docker-clean

# Install dependencies
RUN \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && apt-get install -y \
    --no-install-recommends \
    libgl1-mesa-glx=20.3.* \
    libglib2.0-0=2.66.* \
    libopencv-dev=4.5.* \
  && rm -rf /var/lib/apt/lists/*

######################
### build frontend ###
######################
FROM node:lts as frontend-builder

# Copy Sources
ARG APPDIR=/usr/src
WORKDIR ${APPDIR}
COPY --link . .

# install dependencies and build frontend
WORKDIR ${APPDIR}/invokeai/frontend
RUN \
  --mount=type=cache,target=/usr/local/share/.cache/yarn/v6 \
  yarn install \
  --prefer-offline \
  --frozen-lockfile \
  --non-interactive \
  --production=false \
  && yarn build

###################################
### install python dependencies ###
###################################
FROM python-base AS pyproject-builder

# Install dependencies
RUN \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && apt-get install \
    -yqq \
    --no-install-recommends \
    gcc=4:10.2.* \
    python3-dev=3.9.* \
  && rm -rf /var/lib/apt/lists/*

# create virtual environment
RUN python3 -m venv "${APPNAME}" \
  --upgrade-deps

# copy sources
COPY --from=frontend-builder ${APPDIR} .

# install pyproject.toml
ARG PIP_EXTRA_INDEX_URL
ENV PIP_EXTRA_INDEX_URL ${PIP_EXTRA_INDEX_URL}
RUN --mount=type=cache,target=${PIP_CACHE_DIR},sharing=locked \
  pip install \
  --use-pep517 \
  .

#####################
### runtime image ###
#####################
FROM python-base AS runtime

# setup environment
COPY --from=pyproject-builder ${APPDIR}/${APPNAME} ${APPDIR}/${APPNAME}
ENV INVOKEAI_ROOT=/data
ENV INVOKE_MODEL_RECONFIGURE="--yes --default_only"

# build patchmatch
RUN \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && apt-get install \
    -yqq \
    --no-install-recommends \
    build-essential=12.9 \
  && PYTHONDONTWRITEBYTECODE=1 \
    python3 -c "from patchmatch import patch_match" \
  && apt-get remove -y \
    --autoremove \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# set Entrypoint and default CMD
ENTRYPOINT [ "invokeai" ]
CMD [ "--web", "--host=0.0.0.0" ]
VOLUME [ "/data" ]
