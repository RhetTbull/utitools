# utitools

`utitools` is a simple Python module designed primarily for use on macOS. It allows you to:

- Retrieve the Uniform Type Identifier (UTI) for a given file suffix.
- Get the preferred file extension for a given UTI.

While designed for macOS, `utitools` also works on other platforms by falling back to a cached dictionary for UTI and extension mappings loaded via a CSV file.

## Features

- Works with CoreServices for macOS versions <= 11 (Big Sur) using Objective-C bridge for working with UTIs.
- Uses the `UniformTypeIdentifiers` framework for macOS >= 12 (Monterey).
- On platforms other than macOS, falls back to a cached dictionary for UTI and extension mappings loaded via a CSV file.
- Provides utility functions to convert between file extensions and UTIs.

## Installation

You can install `utitools` from PyPI using pip:

```bash
pip install utitools
```

Alternatively, you can install it from the source code:

1. Clone this repository.
   ```bash
   git clone https://github.com/rhettbull/utitools.git
   ```

2. Install [flit](https://flit.readthedocs.io/en/latest/) if you don't already have it.
   ```bash
   python3 -m pip install flit
   ```

3. Run `flit install` from the root of the repository.
   ```bash
   cd utitools
   flit install
   ```

## Usage

Here are the available functions:

### 1. `uti_for_suffix(suffix: str) -> str | None`

Get the UTI for a given file suffix.

```pycon
>>> from utitools import uti_for_suffix
>>> uti_for_suffix(".jpeg")
'public.jpeg'
>>> uti_for_suffix("jpg")
'public.jpeg'
>>>
```

### 2. `preferred_suffix_for_uti(uti: str) -> str | None`

Get the preferred file extension for a given UTI.

```pycon
>>> from utitools import preferred_suffix_for_uti
>>> preferred_suffix_for_uti("public.jpeg")
'.jpeg'
>>>
```

### 3. `def uti_for_path(path: str | os.PathLike) -> str | None`

Get the UTI for a file at the given path based on its file extension.

```pycon
>>> from utitools import uti_for_path
>>> uti_for_path("/tmp/screenshot.png")
'public.png'
>>>
```

## macOS Version Compatibility

The code path of `utitools` changes depending on the macOS version:

- **macOS ≤ 11 (Big Sur)**: Uses the deprecated methods `UTTypeCopyPreferredTagWithClass` and `UTTypeCreatePreferredIdentifierForTag` from `CoreServices`.
- **macOS ≥ 12 (Monterey)**: Uses the modern `UniformTypeIdentifiers` module.

## Non-macOS Usage

On non-macOS platforms, `utitools` does not have direct access to macOS UTI APIs. Instead, it relies on a cached dictionary loaded from a CSV (`uti.csv`) containing mappings of file extensions and UTIs. This provides a level of compatibility for platforms like Windows or Linux.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to contribute or submit issues via [GitHub issues](https://github.com/rhettbull/utitools/issues).
