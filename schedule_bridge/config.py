from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from semver.version import Version


class PydanticVersion(Version):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls.parse, serialization=core_schema.to_string_ser_schema()
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {
            "type": "string",
            "examples": [
                "1.0.2",
                "2.15.3-alpha",
                "21.3.15-beta+12345",
            ],
        }


__version__ = "0.1.0-alpha"


class Settings(BaseSettings):
    PROJECT_TITLE: str = "schedule-bridge"
    DEBUG: bool = False
    VERSION: PydanticVersion = __version__  # type:ignore
    API_PREFIX: str = "/api"

    model_config = SettingsConfigDict(env_prefix="SCHEDULE_BRIDGE")
