from typing import Callable, Any, Annotated
from pydantic_core import core_schema
from bson import ObjectId as BsonObjectId

# Fast API/ pydantic validation for Mongo DB id

class _ObjectIdPydanticAnnotation:
    # Based on https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types.

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> BsonObjectId:
            return BsonObjectId(input_value)

        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(BsonObjectId),
                core_schema.no_info_plain_validator_function(
                    validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )


PyObjectId = Annotated[
    BsonObjectId, _ObjectIdPydanticAnnotation
]
