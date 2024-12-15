""" Get UTI for a given file suffix and the preferred suffix for a given UTI

    This was designed primarily for use on macOS to get the UTI for a given file suffix and
    the preferred suffix for a given UTI.

    On macOS <= 11 (Big Sur), uses objective C CoreServices methods
    UTTypeCopyPreferredTagWithClass and UTTypeCreatePreferredIdentifierForTag to retrieve the
    UTI and the extension.  These are deprecated in 10.15 (Catalina) and no longer supported on Monterey..

    On macOS >= 12 (Monterey), uses the UniformTypeIdentifiers module to get the UTI and the extension.

    On platforms other than macOS, this module will return use a cached dictionary of UTI to extension mappings.

    The macOS specific methods are wrapped in try/except blocks because they may fail on some versions of macOS.
    They will fallback to the cached versions if an exception is raised.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import pathlib
import sys

from .platform import get_macos_version, is_macos

if is_macos:
    import CoreServices
    import objc
    from CoreFoundation import CFArrayGetCount, CFArrayGetValueAtIndex
    from Foundation import NSString

    try:
        # only available on macOS >= 11
        from UniformTypeIdentifiers import UTType
    except ImportError:
        pass

kUTTypeConformsToKey = "UTTypeConformsTo"

logger = logging.getLogger("utitools")

__all__ = [
    "conforms_to_uti",
    "preferred_suffix_for_uti",
    "uti_for_suffix",
    "uti_for_path",
    "content_type_tree_for_uti",
]

# load CSV separated uti data into dictionaries with key of extension and UTI
UTI_CSV = "uti.csv"
UTI_TREE_JSON = "uti_tree.json"
EXT_UTI_DICT = {}
UTI_EXT_DICT = {}
UTI_CONTENT_TREE = {}


def _load_uti_dict():
    """load an initialize the cached UTI and extension dicts"""
    csv_file = pathlib.Path(__file__).parent / UTI_CSV
    csv_data = csv_file.read_text()
    _reader = csv.DictReader(csv_data.split("\n"), delimiter=",")
    for row in _reader:
        EXT_UTI_DICT[row["extension"]] = row["UTI"]
        UTI_EXT_DICT[row["UTI"]] = row["preferred_extension"]


def _load_uti_tree():
    """Load and initialize the cached UTI content tree dict"""
    global UTI_CONTENT_TREE
    json_file = pathlib.Path(__file__).parent / UTI_TREE_JSON
    UTI_CONTENT_TREE = json.loads(json_file.read_text())


_load_uti_dict()
_load_uti_tree()

# OS version for determining which methods can be used
OS_VER, OS_MAJOR, _ = (
    (int(x) for x in get_macos_version()) if is_macos else (None, None, None)
)


def _get_uti_from_ext_dict(ext):
    try:
        return EXT_UTI_DICT[ext.lower()]
    except KeyError:
        return None


def _get_ext_from_uti_dict(uti):
    try:
        return UTI_EXT_DICT[uti.lower()]
    except KeyError:
        return None


def preferred_suffix_for_uti(uti: str) -> str | None:
    """Get preferred suffix for a UTI type

    Args:
        uti: UTI str, e.g. 'public.jpeg'

    Returns: preferred suffix as str with leading '.' (e.g. '.jpeg') or None if not found.
    """

    if sys.platform != "darwin":
        return _preferred_uti_for_suffix_non_darwin(uti)

    try:
        if (OS_VER, OS_MAJOR) <= (10, 16):
            return _preferred_uti_for_suffix_darwin_10(uti)
        return _preferred_uti_for_suffix_darwin_12(uti)
    except Exception:
        return _preferred_uti_for_suffix_non_darwin(uti)


def uti_for_suffix(suffix: str) -> str | None:
    """Get UTI for a given file suffix.

    Args:
        suffix: file suffix, e.g. 'jpg', 'jpeg', 'heic', etc. with or without leading '.'

    Returns: UTI str or None if UTI cannot be determined
    """

    if not suffix:
        return None

    # accepts extension with or without leading 0
    if suffix[0] == ".":
        suffix = suffix[1:]

    if sys.platform != "darwin":
        return _uti_for_suffix_non_darwin(suffix)

    try:
        if (OS_VER, OS_MAJOR) <= (10, 16):
            return _uti_for_suffix_darwin_10(suffix)
        return _uti_for_suffix_darwin_12(suffix)
    except Exception:
        return _uti_for_suffix_non_darwin(suffix)


def uti_for_path(path: str | os.PathLike) -> str | None:
    """Get UTI for a file at given path or None if UTI cannot be determined"""
    path = path if isinstance(path, pathlib.Path) else pathlib.Path(path)
    return uti_for_suffix(path.suffix)


def _preferred_uti_for_suffix_non_darwin(uti: str) -> str | None:
    if suffix := _get_ext_from_uti_dict(uti):
        return f".{suffix}"
    return None


def _preferred_uti_for_suffix_darwin_10(uti: str) -> str | None:
    # reference: https://developer.apple.com/documentation/coreservices/1442744-uttypecopypreferredtagwithclass?language=objc
    # deprecated in Catalina+, won't work at all on macOS 12+
    with objc.autorelease_pool():
        suffix = CoreServices.UTTypeCopyPreferredTagWithClass(
            uti, CoreServices.kUTTagClassFilenameExtension
        )
        if suffix:
            return f".{suffix}"

        # on MacOS 10.12, HEIC files are not supported and UTTypeCopyPreferredTagWithClass will return None for HEIC
        if uti == "public.heic":
            return ".heic"

        return None


def _preferred_uti_for_suffix_darwin_12(uti: str) -> str | None:
    with objc.autorelease_pool():
        uti_nsstring = NSString.stringWithString_(uti)
        ut_type = UTType.typeWithIdentifier_(uti_nsstring)
        return f".{ut_type.preferredFilenameExtension()}" if ut_type else None


def _uti_for_suffix_non_darwin(suffix: str) -> str | None:
    return _get_uti_from_ext_dict(suffix) or None


def _uti_for_suffix_darwin_10(suffix: str) -> str | None:
    # https://developer.apple.com/documentation/coreservices/1448939-uttypecreatepreferredidentifierf
    with objc.autorelease_pool():
        uti = CoreServices.UTTypeCreatePreferredIdentifierForTag(
            CoreServices.kUTTagClassFilenameExtension, suffix, None
        )
        if uti:
            return uti

        # on MacOS 10.12, HEIC files are not supported and UTTypeCopyPreferredTagWithClass will return None for HEIC
        if suffix.lower() == "heic":
            return "public.heic"

        return None


def _uti_for_suffix_darwin_12(suffix: str) -> str | None:
    with objc.autorelease_pool():
        suffix_nsstring = NSString.stringWithString_(suffix)
        ut_type = UTType.typeWithFilenameExtension_(suffix_nsstring)
        uti = ut_type.identifier() if ut_type else None
        if uti and uti.startswith("dyn."):
            # dynamic UTIs are not useful for file type identification
            uti = None
        return uti


def content_type_tree_for_uti(uti: str) -> list[str]:
    """Return the full UTI conformance tree for a given UTI."""
    if sys.platform != "darwin":
        return _get_full_uti_tree_non_darwin(uti)

    try:
        if (OS_VER, OS_MAJOR) <= (10, 16):
            uti_tree = _get_full_uti_tree_darwin_10(uti)
        else:
            uti_tree = _get_full_uti_tree_darwin_12(uti)
        if not uti_tree:
            return []
        if uti not in uti_tree:
            # add the input UTI to the list
            uti_tree.insert(0, uti)
        return uti_tree
    except Exception:
        return _get_full_uti_tree_non_darwin(uti)


def conforms_to_uti(uti1: str, uti2: str) -> bool:
    """Returns True if uti1 conforms to uti2, False otherwise.

    Example:
        conforms_to('public.jpeg', 'public.image') -> True
    """
    return uti2.lower() in content_type_tree_for_uti(uti1)


def _get_full_uti_tree_non_darwin(uti: str) -> list[str]:
    uti = uti.lower()
    if uti not in UTI_CONTENT_TREE:
        return []
    return UTI_CONTENT_TREE[uti]


def _get_full_uti_tree_darwin_10(uti: str) -> list[str]:
    """Recursively fetches the UTI conformance tree for a given UTI.

    Returns a list of all UTIs that the input UTI conforms to (directly and indirectly).

    Uses an API deprecated in macOS 12.

    Does not include the input UTI in the returned list.
    """
    with objc.autorelease_pool():
        uti_declaration = CoreServices.UTTypeCopyDeclaration(uti)
        if uti_declaration is None:
            return []
        direct_conformances = uti_declaration.get(kUTTypeConformsToKey)
        print(f"{direct_conformances=}")
        if not direct_conformances:
            return []

        if isinstance(direct_conformances, str):
            direct_conformances = [direct_conformances]

        full_uti_tree = list(direct_conformances)

        for parent_uti in direct_conformances:
            # Recursively collect the tree for each parent UTI
            full_uti_tree += _get_full_uti_tree_darwin_10(parent_uti)

        return full_uti_tree


def _get_full_uti_tree_darwin_12(uti):
    """
    Fetches the UTI conformance tree for a given UTI.

    Returns a list of all UTIs that the input UTI conforms to (directly and indirectly),
    using modern UniformTypeIdentifiers API available in macOS >= 12.

    Does not include the input UTI in the returned list.
    """

    with objc.autorelease_pool():
        # Create a UniformType identifiers object
        uti_object = UTType.typeWithIdentifier_(uti)
        # Check if the UTI object is valid
        if not uti_object:
            return []

        # Get direct conformances
        direct_conformances = uti_object.supertypes()
        if not direct_conformances:
            return []

        full_tree = [
            UTType.typeWithIdentifier_(str(uti)) for uti in direct_conformances
        ]

        # Sort according to the `isSubtypeOfType_` method
        ordered_full_tree = sorted(
            full_tree,
            key=lambda item: (
                -sum(1 for uti in full_tree if item.isSubtypeOfType_(uti))
            ),
        )
        return [str(uti.identifier()) for uti in ordered_full_tree]
