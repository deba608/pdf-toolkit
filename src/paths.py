"""Path helpers that work both from source and from a PyInstaller bundle."""
import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """Return the path of a bundled resource.

    In a PyInstaller build ``--add-data=src/resources;resources`` puts the
    folder next to the executable (``_MEIPASS/resources`` in one-file mode),
    so ``__file__``-relative lookups from inside ``src/`` would miss it.
    """
    bundle_root = getattr(sys, "_MEIPASS", None)
    base = Path(bundle_root) if bundle_root else Path(__file__).resolve().parent
    return base.joinpath("resources", *parts)
