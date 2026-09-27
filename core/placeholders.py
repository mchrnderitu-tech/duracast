"""Deterministic placeholder imagery for demo content.

picsum.photos needs no API key and returns a stable image per seed, so the
seeded site is fully populated out of the box. Replace with your own photos
(or direct images.unsplash.com URLs) when available.
"""

PICSUM = "https://picsum.photos/seed/{seed}/{width}/{height}"


def placeholder(seed: str, width: int = 1200, height: int = 800) -> str:
    return PICSUM.format(seed=seed, width=width, height=height)