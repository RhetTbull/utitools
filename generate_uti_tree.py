"""Generate uti_tree.json for use by utitools"""

import utitools
import json

def generate_uti_tree():
    """Generate uti_tree.json for use by utitools"""
    uti_tree = {}
    for uti in utitools.uti.UTI_EXT_DICT:
        uti_tree[uti] = utitools.content_type_tree_for_uti(uti)
    with open("uti_tree.json", "w") as fd:
        json.dump(uti_tree, fd, indent=4)

if __name__ == "__main__":
    generate_uti_tree()
