import importlib.metadata

PROJECT_MODULE = __name__.split(".")[0]
PROJECT_NAME = PROJECT_MODULE.replace("_", "-")
PROJECT_NAME_SHORT = "c-sh"

CONFIG_FILE = "config.yaml"

try:
    VERSION = importlib.metadata.version(PROJECT_NAME)
except importlib.metadata.PackageNotFoundError:
    VERSION = "0.0.0"
