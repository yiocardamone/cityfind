from pydantic import BaseModel
from pydantic_extra_types.coordinate import Coordinate


class City(BaseModel):
    name: str
    coordinate: Coordinate
