#!/usr/bin/env bash

if [[ -z $PIP_EXTRA_INDEX_URL ]]; then
  # Decide which container flavor to build if not specified
  if [[ -z "${CONTAINER_FLAVOR}" ]]; then
    # Check for CUDA and ROCm
    CUDA_AVAILABLE=$(
      python -c "import torch;print(torch.cuda.is_available())"
    )
    ROCM_AVAILABLE=$(
      python -c "import torch;print(torch.version.hip is not None)"
    )
    if ${CUDA_AVAILABLE} && [[ $(uname -s) != "Darwin" ]]; then
      CONTAINER_FLAVOR=cuda
    elif ${ROCM_AVAILABLE} && [[ $(uname -s) != "Darwin" ]]; then
      CONTAINER_FLAVOR=rocm
    else
      CONTAINER_FLAVOR=cpu
    fi
  fi
  # Set PIP_EXTRA_INDEX_URL based on container flavor
  if CONTAINER_FLAVOR=rocm; then
    PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL:-https://download.pytorch.org/whl/rocm}
  elif CONTAINER_FLAVOR=cpu; then
    PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL:-https://download.pytorch.org/whl/cpu}
  fi
fi

# Variables shared by build.sh and run.sh
REPOSITORY_NAME=${REPOSITORY_NAME:-$(basename "$(git rev-parse --show-toplevel)")}
VOLUMENAME=${VOLUMENAME:-${REPOSITORY_NAME,,}_data}
ARCH=${ARCH:-$(uname -m)}
PLATFORM=${PLATFORM:-Linux/${ARCH}}
INVOKEAI_BRANCH=$(git branch --show)
CONTAINER_TAG=${CONTAINER_TAG:-${INVOKEAI_BRANCH##*/}}-${CONTAINER_FLAVOR}
CONTAINER_REGISTRY=${CONTAINER_REGISTRY:-ghcr.io}/$(whoami)
CONTAINER_IMAGE=${CONTAINER_IMAGE:-${CONTAINER_REGISTRY}/${REPOSITORY_NAME,,}:${CONTAINER_TAG}}
