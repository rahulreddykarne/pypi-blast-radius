"""Blast-radius estimation for PyPI package versions.

`deps.dev <https://deps.dev>`_ exposes direct/indirect dependent counts for a
package version. PyPI does not expose reliable reverse-dependent download
totals, so this module keeps the raw counts and derives a conservative impact
proxy from monthly downloads plus dependent counts. Treat the proxy as ranking
evidence, not a precise affected-install count.
"""

from __future__ import annotations

import logging
import math
from typing import Any
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

_DEPS_DEV_DEPENDENTS = (
    "https://api.deps.dev/v3alpha/systems/PYPI/packages/{name}/versions/{version}:dependents"
)
_TIMEOUT = 10
_CACHE: dict[tuple[str, str, int], dict[str, Any]] = {}


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=1, backoff_factor=0.4, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "pypi-blast-radius/0.1"})
    return session


_SESSION = _build_session()


def estimate_blast_radius(
    package: str,
    version: str,
    direct_downloads: int = 0,
    *,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Return a best-effort reverse-dependency impact estimate.

    Parameters
    ----------
    package, version:
        The PyPI package name and exact version to look up on deps.dev.
    direct_downloads:
        Optional monthly download count for the package. When provided, it is
        combined with dependent counts into ``estimated_transitive_downloads``
        and ``total_impact_score``.
    session:
        Optional pre-configured :class:`requests.Session`.

    Returns
    -------
    dict
        Empty dict if inputs are missing or deps.dev has no data. Otherwise:
        ``source``, ``direct_downloads``, ``dependent_count``,
        ``direct_dependent_count``, ``indirect_dependent_count``,
        ``estimated_transitive_downloads``, ``total_impact_score``.
    """
    if not package or not version:
        return {}
    key = (package.lower(), version, int(direct_downloads or 0))
    if key in _CACHE:
        return dict(_CACHE[key])

    data = _fetch_dependent_counts(package, version, session or _SESSION)
    if not data:
        _CACHE[key] = {}
        return {}

    dependent_count = int(data.get("dependentCount") or 0)
    direct_count = int(data.get("directDependentCount") or 0)
    indirect_count = int(data.get("indirectDependentCount") or 0)
    estimated_transitive = _estimate_transitive_downloads(
        int(direct_downloads or 0),
        direct_count,
        indirect_count,
    )
    result = {
        "source": "deps.dev v3alpha dependents",
        "direct_downloads": int(direct_downloads or 0),
        "dependent_count": dependent_count,
        "direct_dependent_count": direct_count,
        "indirect_dependent_count": indirect_count,
        "estimated_transitive_downloads": estimated_transitive,
        "total_impact_score": int(direct_downloads or 0) + estimated_transitive,
    }
    _CACHE[key] = result
    return dict(result)


def clear_cache() -> None:
    """Clear the in-process response cache."""
    _CACHE.clear()


def _fetch_dependent_counts(package: str, version: str, session: requests.Session) -> dict[str, Any]:
    url = _DEPS_DEV_DEPENDENTS.format(
        name=quote(package, safe=""),
        version=quote(version, safe=""),
    )
    try:
        resp = session.get(url, timeout=_TIMEOUT)
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, dict) else {}
    except Exception as exc:  # noqa: BLE001 - network failures are non-fatal
        logger.debug("deps.dev blast-radius query failed for %s==%s: %s", package, version, exc)
        return {}


def _estimate_transitive_downloads(direct_downloads: int, direct_count: int, indirect_count: int) -> int:
    if direct_downloads <= 0 or (direct_count <= 0 and indirect_count <= 0):
        return 0
    weighted_dependents = direct_count + (indirect_count * 0.20)
    multiplier = min(10.0, math.log1p(weighted_dependents) * 0.9)
    return int(direct_downloads * multiplier)
