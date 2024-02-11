from aiohttp import web

from cityfind.handlers.cities import CitiesHandler
from cityfind.handlers.healthcheck import healthcheck


def setup_v1_routes(
    application: web.Application,
) -> None:
    router = application.router
    handler = CitiesHandler(application)

    # /healthcheck
    router.add_get("/healthcheck", healthcheck)

    # /api/v1/cities
    router.add_get("/api/v1/cities", handler=handler.get_city_by_name)
    router.add_post("/api/v1/cities", handler=handler.add_city)
    router.add_delete("/api/v1/cities", handler=handler.delete_city_by_name)

    # /api/v1/cities/find
    router.add_get("/api/v1/cities/find", handler=handler.get_cities)
