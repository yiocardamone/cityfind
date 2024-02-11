from pydantic import BaseModel
from pydantic import RootModel
from pydantic_extra_types.coordinate import Coordinate


class City(BaseModel):
    name: str
    coordinate: Coordinate
