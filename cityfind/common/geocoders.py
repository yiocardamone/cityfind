import logging
from typing import Iterator

import aiohttp
from pydantic import BaseModel
from pydantic import RootModel
from pydantic_extra_types.coordinate import Coordinate
from pydantic_extra_types.coordinate import Latitude
from pydantic_extra_types.coordinate import Longitude
from retry import retry

from cityfind.common.errors import ConfigError
from cityfind.common.errors import GeoCoderNotFoundError
from cityfind.models.config import GeoCoderSetting

_TIMEOUT = 4  # 4 seconds


class _Coordinate(BaseModel):
    lat: float
    lon: float

    def to_pydantic_coordinate(self) -> Coordinate:
        return Coordinate(
            longitude=Longitude(self.lon), latitude=Latitude(self.lat)
        )


class _CoordinateList(RootModel):
    root: list[_Coordinate]


class _IGeoCoderBase:
    API_TYPE: str | None = None

    def __init__(self, key: str):
        self._key = key

    async def request(self, name: str) -> Coordinate:
        raise NotImplementedError()


class _GeocodeMaps(_IGeoCoderBase):
    API_TYPE = "geocode_maps"
    __FORWARD_DECODE_ROUTE_MASK = (
        "https://geocode.maps.co/search?q={city}&api_key={key}"
    )

    async def request(self, name: str) -> Coordinate:

        async with aiohttp.ClientSession() as session:
            route = self.__FORWARD_DECODE_ROUTE_MASK.format(
                city=name, key=self._key
            )
            async with session.get(route) as response:
                response.raise_for_status()
                data = await response.json()
                coordinate_list = _CoordinateList(data)
                if not coordinate_list.root:
                    raise GeoCoderNotFoundError

        coordinate = coordinate_list.root.pop()
        return coordinate.to_pydantic_coordinate()


async def get_coordinate(
    name: str, *geo_coders: GeoCoderSetting
) -> Coordinate:
    resource_iterator = __get_available_resources(*geo_coders)

    @retry(exceptions=(GeoCoderNotFoundError, TimeoutError), delay=_TIMEOUT)
    async def get_result(iterator: Iterator[_IGeoCoderBase]) -> Coordinate:
        resource = next(iterator, None)
        if resource is None:
            raise GeoCoderNotFoundError("Geo coders not available")

        try:
            coordinate = await resource.request(name)
            return coordinate
        except GeoCoderNotFoundError:
            logging.warning("City not found")
            raise

    return await get_result(resource_iterator)


def __get_available_resources(
    *geo_coders: GeoCoderSetting,
) -> Iterator[_IGeoCoderBase]:
    resources_data = {resource.name: resource.key for resource in geo_coders}
    for cls in _IGeoCoderBase.__subclasses__():
        if cls.API_TYPE not in resources_data:
            raise ConfigError(f"{cls.API_TYPE} not represent in config")

        yield cls(key=resources_data[cls.API_TYPE])
