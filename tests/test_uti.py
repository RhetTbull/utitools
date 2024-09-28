"""Test utitools module."""

from unittest.mock import patch

import pytest

from utitools import preferred_suffix_for_uti, uti_for_path, uti_for_suffix

UTI_SUFFIX = [
    ("public.jpeg", ".jpeg"),  # Common UTI
    ("public.png", ".png"),  # Another common UTI
    (
        "public.heic",
        ".heic",
    ),  # heic is a special case on macOS <= 10.12 which don't recognize heic format
    ("public.unknown", None),  # Invalid/unknown UTI
    ("", None),
    ("!@#$%^&*", None),  # Unusual symbols as input
]

SUFFIX_UTI = [
    (".jpeg", "public.jpeg"),  # Valid suffix with leading dot
    ("jpg", "public.jpeg"),  # Valid suffix without leading dot
    (".png", "public.png"),  # Valid suffix with leading dot
    (
        ".heic",
        "public.heic",
    ),  # heic is a special case on macOS <= 10.12 which don't recognize heic format
    ("unknown", None),  # Unknown suffix
    ("", None),  # Empty string
    ("!@#$%^&*", None),  # Unusual symbols as input
]

PATH_UTI = [
    ("/Users/doe/Desktop/image.jpg", "public.jpeg"),  # Valid suffix with leading dot
    ("~/Downloads/screenshot.png", "public.png"),  # Valid suffix with leading dot
    ("/Users/does/Desktop/foo", None),  # no suffix
]


@pytest.mark.parametrize("uti, expected_suffix", UTI_SUFFIX)
def test_get_preferred_uti_suffix(uti, expected_suffix):
    """Test preferred_suffix_for_uti."""
    assert preferred_suffix_for_uti(uti) == expected_suffix


@pytest.mark.parametrize("uti, expected_suffix", UTI_SUFFIX)
def test_get_preferred_uti_suffix_linux(uti, expected_suffix):
    """Test preferred_suffix_for_uti on-Darwin code path even if running on macOS."""
    with patch("sys.platform", "linux"):
        assert preferred_suffix_for_uti(uti) == expected_suffix


@pytest.mark.parametrize("suffix, expected_uti", SUFFIX_UTI)
def test_get_uti_for_suffix(suffix, expected_uti):
    """Test uti_for_suffix."""
    assert uti_for_suffix(suffix) == expected_uti


@pytest.mark.parametrize("suffix, expected_uti", SUFFIX_UTI)
def test_get_uti_for_suffix_linux(suffix, expected_uti):
    """Test uti_for_suffix on-Darwin code path even if running on macOS."""
    with patch("sys.platform", "linux"):
        assert uti_for_suffix(suffix) == expected_uti


@pytest.mark.parametrize("path, expected_uti", PATH_UTI)
def test_uti_for_path(path, expected_uti):
    """Test uti_for_path."""
    assert uti_for_path(path) == expected_uti
