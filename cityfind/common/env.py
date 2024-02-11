import os
from enum import Enum


class EnvironmentVariable(Enum):
    CONFIG_RELATIVE_PATH = "CITYFIND_CONFIG_PATH"
    LOGGING_RELATIVE_PATH = "CITYFIND_LOGGING_INI_PATH"


def load_env_variable(variable: EnvironmentVariable) -> str | None:
    return os.environ.get(variable.value)
