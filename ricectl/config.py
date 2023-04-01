from pathlib import Path
from typing import Dict, Any

from pydantic import BaseSettings
import toml
from xdg_base_dirs import xdg_config_home, xdg_config_dirs


class Config(BaseSettings):
    """Configuration options for ricectl"""

    repo: Path = Path("/opt/rice")
    """ The location where the rice repo lives """

    class Config:
        env_prefix = "RICE_"
        """ Environment variable prefix """
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                init_settings,
                xdg_toml_settings_source,
                env_settings,
                file_secret_settings,
            )


def xdg_toml_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    Load settings from a configuration file under one of the XDG config directories.

    Precedence is given to the XDG_CONFIG_HOME, and then to system XDG directories.
    """

    for path in [xdg_config_home(), list(xdg_config_dirs())]:
        try:
            with (path / "rice" / "config.toml").open(
                "r", encoding=settings.__config__.env_file_encoding
            ) as filp:
                return toml.load(filp)
        except (PermissionError, FileNotFoundError):
            continue

    return {}
