"""Pydantic models."""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import StrEnum

from datetime import timezone, datetime

from pydantic import SecretStr, computed_field, Field, BaseModel, model_validator
from typing import Tuple, Type

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)


class EnvFileModel(BaseSettings):
    """Environmental Variable model read from .env file."""

    model_config = SettingsConfigDict(env_file=Path.cwd() / '.env', env_file_encoding='utf-8', extra='allow')
    # env var from .env file declared as Optional[str] = None or Optional[SecretStr] = None
    # others will be loaded as extra


class EnvVars(BaseSettings):
    """Environmental Variable model."""

    model_config = SettingsConfigDict(extra='allow')
    # env var coming from environment
    ci: Optional[str] = None
    git_commit: Optional[str] = None


class TomlSettings(BaseSettings):
    """Base class to read toml files as pyproject.toml ."""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)


class PoetrySettings(TomlSettings):
    """Subclass to manage poetry table from pyproject.toml ."""

    model_config = SettingsConfigDict(
        pyproject_toml_table_header=('tool', 'poetry'),
        extra='allow'
    )


class PyProjectAuthors(BaseSettings):
    """Model used into project table."""

    name: str
    email: str

    def __str__(self):
        return f"{self.name} <{self.email}>"


class PyProjectLicense(BaseSettings):
    """Model used into project table."""

    text: str


class PyProjectURLs(BaseSettings):
    """Model used into project table."""

    homepage: str
    repository: str
    documentation: str
    bug_tracker: str = Field(alias='Bug Tracker')
    changelog: str
    docker: str


class PyprojectSettings(TomlSettings):
    """Subclass to manage project table from pyproject.toml ."""

    model_config = SettingsConfigDict(
        pyproject_toml_table_header=(('project',)),
        extra='allow'
    )

    name: str
    version: str
    description: str
    authors: List[PyProjectAuthors]
    license: PyProjectLicense
    urls: PyProjectURLs


class SubModels(StrEnum):
    """Sum models enum."""

    env_file = "env_file"
    env_vars = "env_vars"
    pyproject_settings = "pyproject_settings"
    poetry_settings = "poetry_settings"


class PyprojectModel(BaseModel):
    """Entire pyproject.toml file model."""

    pyproject_settings: PyprojectSettings
    poetry_settings: PoetrySettings
    env_file: EnvFileModel
    env_vars: EnvVars

    IMAGE_TIMESTAMP: str
    IMAGE_NAME: str
    IMAGE_VERSION: str
    IMAGE_SRC: str
    IMAGE_DOC: str
    IMAGE_DESCRIPTION: str
    IMAGE_AUTHORS: str
    IMAGE_LICENSE: str
    IMAGE_URL: str
    IMAGE_GIT_HASH: Optional[str] = None

    def __init__(self, **data):
        if SubModels.env_file not in data:
            data[SubModels.env_file] = EnvFileModel()
        if SubModels.env_vars not in data:
            data[SubModels.env_vars] = EnvVars(**os.environ)
        if SubModels.pyproject_settings not in data:
            data[SubModels.pyproject_settings] = PyprojectSettings()
        if SubModels.poetry_settings not in data:
            data[SubModels.poetry_settings] = PoetrySettings()

        super().__init__(**data)

    @model_validator(mode='before')
    @classmethod
    def flatten_args(cls, data: Any) -> Any:
        """Validate parameters making the submodels and the explicit variables."""

        if isinstance(data, dict):
            _env_f = data.get(SubModels.env_file)
            if _env_f is None:
                return data
            _env_file = EnvFileModel.model_validate(_env_f)

            _env_v = data.get(SubModels.env_vars)
            if _env_v is None:
                return data
            _env_vars = EnvVars.model_validate(_env_v)

            _pyproj = data.get(SubModels.pyproject_settings)
            if _pyproj is None:
                return data
            _pypr = PyprojectSettings.model_validate(_pyproj)

            _poetry = data.get(SubModels.poetry_settings)
            if _poetry is None:
                return data
            _poetry_sett = PoetrySettings.model_validate(_poetry)

            return {
                "IMAGE_TIMESTAMP": datetime.now(timezone.utc).isoformat(),
                "IMAGE_NAME": _pypr.name,
                "IMAGE_VERSION": _pypr.version,
                "IMAGE_SRC": _pypr.urls.repository,
                "IMAGE_DOC": _pypr.urls.documentation,
                "IMAGE_DESCRIPTION": _pypr.description,
                "IMAGE_AUTHORS": ', '.join([str(_a) for _a in _pypr.authors]),
                "IMAGE_LICENSE": _pypr.license.text,
                "IMAGE_URL": _pypr.urls.docker,
                "IMAGE_GIT_HASH": _env_vars.git_commit,
            } | dict(data)



#####  other pydantic models...
