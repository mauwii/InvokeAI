"""
ldm.invoke.globals defines a small number of global variables that would
otherwise have to be passed through long and complex call chains.

It defines a Namespace object named "Globals" that contains
the attributes:

  - root           - the root directory under which "models" and "outputs" can be found
  - initfile       - path to the initialization file
  - try_patchmatch - option to globally disable loading of 'patchmatch' module
  - always_use_cpu - force use of CPU even if GPU is available
"""

import os
import os.path as osp
from argparse import Namespace
from pathlib import Path
from typing import Union

Globals = Namespace()

# This is usually overwritten by the command line and/or environment variables
if os.environ.get("INVOKEAI_ROOT"):
    Globals.root = osp.abspath(os.path.expanduser(os.environ["INVOKEAI_ROOT"]))
elif os.environ.get("VIRTUAL_ENV"):
    Globals.root = osp.abspath(osp.join(os.environ["VIRTUAL_ENV"], ".."))
else:
    Globals.root = osp.abspath(osp.expanduser("~/invokeai"))

# Where to look for the initialization file
Globals.initfile = "invokeai.init"
Globals.models_file = "models.yaml"
Globals.models_dir = "models"
Globals.config_dir = "configs"
Globals.autoscan_dir = "weights"
Globals.converted_ckpts_dir = "converted-ckpts"

# Try loading patchmatch
Globals.try_patchmatch = True

# Use CPU even if GPU is available (main use case is for debugging MPS issues)
Globals.always_use_cpu = False

# Whether the internet is reachable for dynamic downloads
# The CLI will test connectivity at startup time.
Globals.internet_available = True

# Whether to disable xformers
Globals.disable_xformers = False

# whether we are forcing full precision
Globals.full_precision = False


def global_config_file() -> Path:
    return Path(Globals.root, Globals.config_dir, Globals.models_file)


def global_config_dir() -> Path:
    return Path(Globals.root, Globals.config_dir)


def global_models_dir() -> Path:
    return Path(Globals.root, Globals.models_dir)


def global_autoscan_dir() -> Path:
    return Path(Globals.root, Globals.autoscan_dir)


def global_set_root(root_dir: Union[str, Path]):
    Globals.root = root_dir


def global_cache_dir(subdir: Union[str, Path] = "") -> Path:
    """
    Returns Path to the model cache directory. If a subdirectory
    is provided, it will be appended to the end of the path, allowing
    for huggingface-style conventions:
         global_cache_dir('diffusers')
         global_cache_dir('hub')
    Current HuggingFace documentation (mid-Jan 2023) indicates that
    transformers models will be cached into a "transformers" subdirectory,
    but in practice they seem to go into "hub". But if needed:
         global_cache_dir('transformers')
    One other caveat is that HuggingFace is moving some diffusers models
    into the "hub" subdirectory as well, so this will need to be revisited
    from time to time.
    """

    if os.getenv("HF_HOME"):
        home = osp.abspath(os.path.expanduser(os.environ["HF_HOME"]))

    elif os.getenv("XDG_CACHE_HOME"):
        # Set `home` to $XDG_CACHE_HOME/huggingface, which is the default location mentioned in HuggingFace Hub Client Library.
        # See: https://huggingface.co/docs/huggingface_hub/main/en/package_reference/environment_variables#xdgcachehome
        home = osp.abspath(
            osp.join(os.path.expanduser(os.environ["XDG_CACHE_HOME"]), "huggingface")
        )

    else:
        home = osp.abspath(osp.join(Globals.root, "models"))

    return Path(home, subdir)
