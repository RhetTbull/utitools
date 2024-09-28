""" Get UTI for a given file suffix and the preferred suffix for a given UTI

    This was designed primarily for use on macOS to get the UTI for a given file suffix and
    the preferred suffix for a given UTI.

    On macOS <= 11 (Big Sur), uses objective C CoreServices methods
    UTTypeCopyPreferredTagWithClass and UTTypeCreatePreferredIdentifierForTag to retrieve the
    UTI and the extension.  These are deprecated in 10.15 (Catalina) and no longer supported on Monterey..

    On macOS >= 12 (Monterey), uses the UniformTypeIdentifiers module to get the UTI and the extension.

    On platforms other than macOS, this module will return use a cached dictionary of UTI to extension mappings.
"""

from __future__ import annotations

import csv
import logging
import os
import pathlib
import sys

from .platform import get_macos_version, is_macos

if is_macos:
    import CoreServices
    import objc
    from Foundation import NSString

    try:
        # only available on macOS >= 11
        from UniformTypeIdentifiers import UTType
    except ImportError:
        pass

logger = logging.getLogger("utitools")

__all__ = ["preferred_suffix_for_uti", "uti_for_suffix", "uti_for_path"]

# load CSV separated uti data into dictionaries with key of extension and UTI
UTI_CSV = "uti.csv"
EXT_UTI_DICT = {}
UTI_EXT_DICT = {}


def _load_uti_dict():
    """load an initialize the cached UTI and extension dicts"""
    csv_file = pathlib.Path(__file__).parent / UTI_CSV
    csv_data = csv_file.read_text()
    _reader = csv.DictReader(csv_data.split("\n"), delimiter=",")
    for row in _reader:
        EXT_UTI_DICT[row["extension"]] = row["UTI"]
        UTI_EXT_DICT[row["UTI"]] = row["preferred_extension"]


_load_uti_dict()

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

    if (OS_VER, OS_MAJOR) <= (10, 16):
        return _preferred_uti_for_suffix_darwin_10(uti)
    return _preferred_uti_for_suffix_darwin_12(uti)


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

    if (OS_VER, OS_MAJOR) <= (10, 16):
        return _uti_for_suffix_darwin_10(suffix)
    return _uti_for_suffix_darwin_12(suffix)


def uti_for_path(path: str | pathlib.Path | os.PathLike) -> str | None:
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
