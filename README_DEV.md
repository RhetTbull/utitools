# Developer Notes

These notes are for developers who want to contribute to the project and for me to remember how to do things.

## Setting up the development environment

python3 -m pip install flit
flit install --symlink

## Building the project

utitools uses [flit](https://flit.readthedocs.io/en/latest/) to build the project. To build the project, run the following command:

```bash
flit build
```

## Docs

Build docs with `mkdocs build` then deploy to GitHub pages with `mkdocs gh-deploy`

## Testing

Testing uses pytest. Use --doctest-glob to include the README.md file.

- `pytest --doctest-glob="*.md"`

## Publishing to PyPI

Update version using `bump-my-version bump minor --verbose`. (minor, major, patch, etc., use --dry-run if desired to see what will be changed)

Add and commit changes to git.

Then `flit build` followed by `flit publish`.

## Generating the uti.csv file

Run the script `generate_uti_csv.py` on macOS which will generate the file uti.csv. Move this file to the `src/utitools/uti.csv`
