import logging
import logging.config
import os

import yaml
from aiohttp import web

from cityfind.common.env import EnvironmentVariable
from cityfind.common.env import load_env_variable
from cityfind.database import Database
from cityfind.models.config import Config
from cityfind.routes import setup_v1_routes

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


def start() -> None:
    _init_logging()
    try:
        config = _load_config()
    except Exception:
        logging.fatal("Configuration loading error")
        raise
    else:
        logging.info("Configuration started successfully")

    application = web.Application()
    application["config"] = config
    application["database"] = Database(config.redis)

    setup_v1_routes(application)
    web.run_app(application, host=config.server.host, port=config.server.port)


def _init_logging() -> None:
    relative_path = load_env_variable(
        EnvironmentVariable.LOGGING_RELATIVE_PATH
    )
    assert relative_path is not None

    path = os.path.join(PROJECT_ROOT, relative_path)
    os.path.join(PROJECT_ROOT, "logging.ini")
    logging.config.fileConfig(path)


def _load_config() -> Config:
    relative_path = load_env_variable(EnvironmentVariable.CONFIG_RELATIVE_PATH)
    assert relative_path is not None

    path = os.path.join(PROJECT_ROOT, relative_path)
    with open(path, "r") as file:
        data = yaml.safe_load(file)

    return Config.model_validate(data)
