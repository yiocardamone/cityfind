import dataclasses

from pydantic import BaseModel


class GeoCoderSetting(BaseModel):
    name: str
    key: str


class LoggerSettings(BaseModel):
    config_file: str
    logs_path: str


@dataclasses.dataclass
class Address(BaseModel):
    host: str
    port: int


@dataclasses.dataclass
class Config(BaseModel):
    server: Address
    redis: Address
    logger: LoggerSettings
    geo_coders: tuple[GeoCoderSetting]
