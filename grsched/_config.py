from typing import Final

from appconfigpy import ConfigItem, ConfigManager, DefaultDisplayStyle

from ._const import MODULE_NAME


class ConfigKey:
    SUBDOMAIN: Final[str] = "subdomain"
    BASIC_AUTH: Final[str] = "basic_auth"


app_config_mgr = ConfigManager(
    MODULE_NAME,
    [
        ConfigItem(
            name=ConfigKey.SUBDOMAIN,
            prompt_text="subdomain",
            initial_value="",
        ),
        ConfigItem(
            name=ConfigKey.BASIC_AUTH,
            prompt_text="basic auth info (base64 encoded 'login-name:passowrd')",
            initial_value="",
            default_display_style=DefaultDisplayStyle.PART_VISIBLE,
        ),
    ],
)
