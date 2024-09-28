"""Test utitools module."""

import pytest
from utitools import preferred_suffix_for_uti, uti_for_suffix

UTI_SUFFIX = [
    ("public.jpeg", ".jpeg"),  # Common UTI
    ("public.png", ".png"),  # Another common UTI
    ("public.unknown", None),  # Invalid/unknown UTI
    ("", None),
]

SUFFIX_UTI = [
    (".jpeg", "public.jpeg"),  # Valid suffix with leading dot
    ("jpg", "public.jpeg"),  # Valid suffix without leading dot
    (".png", "public.png"),  # Valid suffix with leading dot
    ("unknown", None),  # Unknown suffix
    ("", None),  # Empty string
    ("!@#$%^&*", None),  # Unusual symbols as input
]


@pytest.mark.parametrize("uti, expected_suffix", UTI_SUFFIX)
def test_get_preferred_uti_suffix(uti, expected_suffix):
    assert preferred_suffix_for_uti(uti) == expected_suffix


@pytest.mark.parametrize("suffix, expected_uti", SUFFIX_UTI)
def test_get_uti_for_suffix(suffix, expected_uti):
    assert uti_for_suffix(suffix) == expected_uti
