import logging
from typing import Mapping
from typing import TypeVar

from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_exceptions import HTTPNotFound
from pydantic import BaseModel
from pydantic import ValidationError
from pydantic_extra_types.coordinate import Coordinate

from cityfind.common.errors import DatabaseNotFoundError
from cityfind.common.errors import GeoCoderNotFoundError
from cityfind.common.geocoders import get_coordinate
from cityfind.database import Database
from cityfind.models.cities import City
from cityfind.models.config import Config

routes = web.RouteTableDef()

T = TypeVar("T")


class _CityQuery(BaseModel):
    name: str


class CitiesHandler:
    def __init__(self, application: web.Application):
        self.__database: Database = application["database"]
        self.__config: Config = application["config"]

    async def get_cities(self, request: web.Request) -> web.Response:
        coordinate = self.__validated_data(request.query, Coordinate)

        try:
            result = await self.__database.get_nearest_cities_by_coordinate(
                coordinate=coordinate,
            )
        except DatabaseNotFoundError as e:
            logging.info(e)
            raise HTTPNotFound

        return web.Response(text=",".join(result))

    async def get_city_by_name(self, request: web.Request) -> web.Response:
        query: _CityQuery = self.__validated_data(request.query, _CityQuery)

        try:
            result = await self.__database.get_city_by_name(query.name)
        except DatabaseNotFoundError as e:
            logging.info(e)
            raise HTTPNotFound

        return web.json_response(data=result.model_dump())

    async def add_city(self, request: web.Request) -> web.Response:
        geo_coders = self.__config.geo_coders
        query: _CityQuery = self.__validated_data(request.query, _CityQuery)

        try:
            city = City(
                name=query.name,
                coordinate=await get_coordinate(query.name, *geo_coders),
            )
        except GeoCoderNotFoundError as e:
            logging.info(e)
            raise HTTPNotFound

        await self.__database.add_city(city)
        return web.Response(text="Created", status=201)

    async def delete_city_by_name(self, request: web.Request) -> web.Response:
        query: _CityQuery = self.__validated_data(request.query, _CityQuery)
        await self.__database.delete_city_by_name(query.name)
        return web.Response(status=202)

    @staticmethod
    def __validated_data(data: Mapping, type_name: type[T]) -> T:
        if not data:
            raise HTTPBadRequest(text="Insufficient parameters")

        try:
            result = type_name(**data)
        except ValidationError as e:
            raise HTTPBadRequest(text=str(e))
        except Exception:
            raise HTTPBadRequest(text=f"Incorrect data: {str(data)}")
        else:
            return result
