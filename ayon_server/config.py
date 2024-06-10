"""Server configuration object"""

import os

from aiocache import caches
from pydantic import BaseModel, Field

caches.set_config(
    {
        "default": {
            "cache": "aiocache.SimpleMemoryCache",
            "serializer": {"class": "aiocache.serializers.StringSerializer"},
        },
    }
)


class AyonConfig(BaseModel):
    """Server configuration"""

    http_listen_address: str = Field(
        default="0.0.0.0",
        description="An address the API server listens on",
    )

    http_listen_port: int = Field(
        default=5000,
        description="A port the API server listens on",
    )

    api_modules_dir: str = Field(
        default="api",
        description="Path to the directory containing the API modules.",
    )

    project_data_dir: str = Field(
        default="/storage/server/projects",
        description="Path to the directory containing the project files."
        " such as comment attachments, thumbnails, etc.",
    )

    avatar_dir: str = Field(
        default="/storage/server/avatars",
        description="Path to the directory containing the user avatars.",
    )

    addons_dir: str = Field(
        default="/addons",
        description="Absolute path to the directory containing the addons.",
    )

    frontend_dir: str = Field(
        default="/frontend",
        description="Path to the directory containing the frontend files.",
    )

    auth_pass_pepper: str = Field(
        default="supersecretpasswordpepper",
        description="A secret string used to salt the password hash.",
    )

    auth_pass_min_length: int = Field(
        default=8,
        description="Minimum password length.",
    )

    auth_pass_complex: str = Field(
        default=True,
        description="Enforce using a complex password.",
    )

    redis_url: str = Field(
        default="redis://redis/",
        description="Connection string for Redis.",
        example="redis://user:password123@redis.example.com:6379",
    )

    redis_channel: str = Field(
        default="pype:c",
        description="Redis channel name for system messages",
    )

    redis_key_prefix: str | None = Field(
        default=None,
        description="Redis keys prefix",
    )

    postgres_url: str = Field(
        default="postgres://ayon:ayon@postgres/ayon",
        description="Connection string for Postgres.",
        example="postgres://user:password123@postgres.example.com:5432/ayon",
    )

    session_ttl: int = Field(
        default=24 * 3600,
        description="Session lifetime in seconds",
    )

    disable_check_session_ip: bool = Field(
        default=False,
        description="Skip checking session IP match real IP",
    )

    max_failed_login_attempts: int = Field(
        default=10,
        description="Maximum number of failed login attempts",
    )

    failed_login_ban_time: int = Field(
        default=600,
        description="Interval in seconds to ban IP addresses "
        "with too many failed login attempts",
    )

    motd: str | None = Field(
        default=None,
        description="Message of the day",
        example="Welcome to Ayon!",
    )

    motd_path: str | None = Field(
        default="/storage/motd.md",
        description="Path to the MOTD file",
    )

    login_page_background: str | None = Field(
        default=None,
        description="Login page background image",
        example="https://example.com/background.jpg",
    )

    login_page_brand: str | None = Field(
        default=None,
        description="Login page brand image",
        example="https://example.com/brand.png",
    )

    geoip_db_path: str = Field(
        default="/storage/GeoLite2-City.mmdb",
        description="Path to the GeoIP database",
    )

    force_create_admin: bool = Field(
        default=False,
        description="Ensure creation of admin user on first run",
    )

    disable_rest_docs: bool = Field(
        default=False,
        description="Disable REST API documentation",
    )

    audit_trail: bool = Field(
        default=True,
        description="Enable audit trail",
    )

    log_retention_days: int = Field(
        default=7,
        description="Number of days to keep logs in the event log",
    )

    ynput_cloud_api_url: str | None = Field(
        "https://im.ynput.cloud",
        description="YnputConnect URL",
    )

    http_timeout: int = Field(
        default=120,
        description="Timeout for HTTP requests the server uses "
        "to connect to external services",
    )

    log_file: str | None = Field(
        default=None,
        description="Path to the log file",
    )

    metrics_api_key: str | None = Field(
        default=None,
        description="API key allowing access to the system metrics endpoint",
    )

    email_from: str = Field("noreply@ynput.cloud", description="Email sender address")
    email_smtp_host: str | None = Field(None, description="SMTP server hostname")
    email_smtp_port: int | None = Field(None, description="SMTP server port")
    email_smtp_tls: bool = Field(False, description="Use SSL for SMTP connection")
    email_smtp_user: str | None = Field(None, description="SMTP server username")
    email_smtp_pass: str | None = Field(None, description="SMTP server password")


#
# Load configuration from environment variables
#


def load_config() -> AyonConfig:
    """Load configuration"""
    prefix = "ayon_"
    env_data = {}
    for key, value in dict(os.environ).items():
        if not key.lower().startswith(prefix):
            continue

        key = key.lower().removeprefix(prefix)
        if key in AyonConfig.__fields__:
            env_data[key] = value

    config = AyonConfig(**env_data)

    if (config.motd) is None and (config.motd_path is not None):
        if os.path.exists(config.motd_path):
            with open(config.motd_path) as motd_file:
                config.motd = motd_file.read()

    return config


ayonconfig = load_config()
