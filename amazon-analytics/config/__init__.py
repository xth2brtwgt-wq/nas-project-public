"""Configuration package"""
from .settings import settings
from .version import VERSION, get_version_info, get_full_version

__all__ = ["settings", "VERSION", "get_version_info", "get_full_version"]

