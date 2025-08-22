from pydantic import (
    BaseSettings,
)
from semver.version import Version


class PydanticVersion(Version):
    @classmethod
    def _parse(cls, version):
        return cls.parse(version)

    @classmethod
    def __get_validators__(cls):
        """Return a list of validator methods for pydantic models."""
        yield cls._parse

    @classmethod
    def __modify_schema__(cls, field_schema):
        """Inject/mutate the pydantic field schema in-place."""
        field_schema.update(
            examples=[
                "1.0.2",
                "2.15.3-alpha",
                "21.3.15-beta+12345",
            ]
        )


__version__ = "0.1.0-alpha"


class Settings(BaseSettings):
    PROJECT_TITLE: str = "schedule-bridge"
    DEBUG: bool = False
    VERSION: PydanticVersion = __version__  # type:ignore
    API_PREFIX = "/api"

    class Config:
        env_prefix = "SCHEDULE_BRIDGE"
