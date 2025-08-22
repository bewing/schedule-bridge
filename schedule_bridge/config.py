from typing import Any

from pydantic_settings import (
    BaseSettings,
)
from pydantic_core import CoreSchema
from pydantic import GetJsonSchemaHandler
from semver.version import Version


class PydanticVersion(Version):
    @classmethod
    def _parse(cls, version, optional_minor_and_patch: bool = False):
        return cls.parse(version)

    @classmethod
    def __get_validators__(cls):
        """Return a list of validator methods for pydantic models."""
        yield cls._parse

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler.resolve_ref_schema(core_schema)
        """Inject/mutate the pydantic field schema in-place."""
        json_schema.update(
            examples=[
                "1.0.2",
                "2.15.3-alpha",
                "21.3.15-beta+12345",
            ]
        )
        return json_schema


__version__ = "0.1.0-alpha"


class Settings(BaseSettings):
    PROJECT_TITLE: str = "schedule-bridge"
    DEBUG: bool = False
    VERSION: PydanticVersion = __version__  # type:ignore
    API_PREFIX: str = "/api"

    class Config:
        env_prefix: str = "SCHEDULE_BRIDGE"
