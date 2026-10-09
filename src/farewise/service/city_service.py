from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml


@lru_cache(maxsize=1)
def _city_config() -> dict[str, object]:
    path = Path("configs/cities.yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def get_indian_cities() -> list[str]:
    """Return searchable city destinations from the static Indian airport catalog."""
    config = _city_config()
    cities = {str(city) for city in config["cities"]}
    primary = ["Delhi", "Mumbai", "Bengaluru", "Kolkata", "Hyderabad", "Chennai"]
    return [city for city in primary if city in cities] + sorted(cities - set(primary))


def canonical_city(city: str, known_cities: set[str] | None = None) -> str:
    """Map a catalog display name to the historical spelling used by source data."""
    aliases = _city_config().get("aliases", {})
    canonical = str(aliases.get(city, city))
    if known_cities is not None and canonical.casefold() not in {item.casefold() for item in known_cities}:
        return city
    return canonical
