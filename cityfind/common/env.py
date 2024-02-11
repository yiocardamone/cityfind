import os
from enum import Enum


class EnvironmentVariable(Enum):
    CONFIG_RELATIVE_PATH = "CITYFIND_CONFIG_PATH"
    LOGGING_RELATIVE_PATH = "CITYFIND_LOGGING_INI_PATH"


_DEFAULTS = {
    EnvironmentVariable.CONFIG_RELATIVE_PATH.value: "configs/config.yaml",
    EnvironmentVariable.LOGGING_RELATIVE_PATH.value: "configs/logging.ini"
}


def load_env_variable(variable: EnvironmentVariable) -> str | None:
    return os.environ.get(variable.value, _DEFAULTS.get(variable.value))
