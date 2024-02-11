import logging

from pydantic_extra_types.coordinate import Coordinate
from pydantic_extra_types.coordinate import Latitude
from pydantic_extra_types.coordinate import Longitude
from redis import asyncio as aioredis

from cityfind.common.errors import DatabaseNotFoundError
from cityfind.models.cities import City
from cityfind.models.config import Address

_GEOSET = "cities"
_MAX_RADIUS = 6371
_MIN_RADIUS = 2
_MAX_RESULT = 2


class Database:

    def __init__(self, address: Address):
        self.__redis_url = f"redis://{address.host}:{address.port}"
        self.__redis = aioredis.from_url(self.__redis_url)

    async def get_city_by_name(self, name: str) -> City:
        positions = await self.__redis.geopos(_GEOSET, name)
        if not positions:
            raise DatabaseNotFoundError()

        lat, lon = positions.pop()
        return City(
            name=name,
            coordinate=Coordinate(
                latitude=Latitude(lat), longitude=Longitude(lon)
            ),
        )

    async def get_nearest_cities_by_coordinate(
        self, coordinate: Coordinate
    ) -> set[str]:
        radius = _MIN_RADIUS
        result: set = set()
        while radius <= _MAX_RADIUS or len(result) >= _MAX_RESULT:
            radius **= 2
            names = await self.__redis.georadius(
                _GEOSET,
                coordinate.latitude,
                coordinate.longitude,
                radius,
                "km",
            )
            for name in names:
                result.add(name.decode())

        if not result:
            raise DatabaseNotFoundError()
        return result

    async def add_city(self, city: City) -> None:
        values = (
            city.coordinate.latitude,
            city.coordinate.longitude,
            city.name,
        )
        try:
            await self.__redis.geoadd(_GEOSET, values)
        except Exception as e:
            logging.info(e)

    async def delete_city_by_name(self, name: str) -> None:
        await self.__redis.zrem(_GEOSET, name)
