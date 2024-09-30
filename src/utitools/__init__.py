"""Utilities for working with Universal Type Identifiers (UTIs)"""

__version__ = "0.1.0"

from .uti import (
    conforms_to_uti,
    content_type_tree_for_uti,
    preferred_suffix_for_uti,
    uti_for_path,
    uti_for_suffix,
)

__all__ = [
    "conforms_to_uti",
    "preferred_suffix_for_uti",
    "uti_for_suffix",
    "uti_for_path",
    "content_type_tree_for_uti",
]
