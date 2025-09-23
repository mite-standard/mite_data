# Overview

[![DOI](https://zenodo.org/badge/834042284.svg)](https://zenodo.org/doi/10.5281/zenodo.13294303)

This repository contains the **"ground truth"** dataset of the Minimum Information about a Tailoring Enzyme (MITE) data repository (`mite_data/data`).

Furthermore, the repository contains auxiliary files and scripts to automatically update them:

- Metadata files summarizing information of all MITE entries in a single file (`mite_data/metadata`)
- Protein FASTA-files for all active (i.e. non-retired) MITE entries (`mite_data/fasta`)

For more information on MITE, see the README of the [MITE-Standard organisation page](https://github.com/mite-standard).

## For developers

*Nota bene*: This installation will only work on (Ubuntu) Linux and assumes a Python installation.

```commandline
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run pre-commit install
uv run pytest
```

### Adding/modifying entries

- (Create a new branch)
- Update version in `pyproject.toml`, add changelog to `CHANGELOG.md`
- Reinstall the package to update version metadata: `uv sync`
- Add new/modify existing entries (*N.B. for new entries, change `accession` and `status`*)
- Pre-commit will automatically validate and update metadata files upon committing
- If `pre-commit` was not installed, these steps need to be performed manually:

```commandline
uv run python ./mite_data/main.py
uv run python .github/mite_validation.py
```
