"""pypi-blast-radius: estimate the downstream impact of a PyPI package version.

Public API
----------
- :func:`estimate_blast_radius` – deps.dev dependent counts + impact proxy.
- :func:`clear_cache` – drop the in-process response cache.
"""

from __future__ import annotations

from ._core import clear_cache, estimate_blast_radius

__all__ = ["estimate_blast_radius", "clear_cache"]
__version__ = "0.1.0"
