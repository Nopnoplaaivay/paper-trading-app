from typing import Dict, TypeVar, Generic

from pydantic import BaseModel, ValidationError, Extra


T = TypeVar("T")


class BaseDTO(Generic[T], BaseModel):
    class Config:
        allow_population_by_field_name = True
        orm_mode = False
        # validate_assignment = True
        arbitrary_types_allowed = True
        # anystr_strip_whitespace = True
        extra = Extra.ignore

    def __init__(self, **data):
        try:
            for attr in self.__class__.__fields__:
                value = data.get(attr, None)
                if value is None:
                    default_factory = self.__class__.__fields__[attr].default_factory
                    if default_factory is not None:
                        data[attr] = default_factory()
                    default = self.__class__.__fields__[attr].default
                    if default is not None:
                        data[attr] = default
            print("new DTO worked", data)
            super().__init__(**data)
        except ValidationError as exception:
            raise exception
        except Exception as exception:
            raise exception
