mite_extras
=========

[![DOI](https://zenodo.org/badge/834042284.svg)](https://zenodo.org/doi/10.5281/zenodo.13294303)

Contents
-----------------
- [Overview](#overview)
- [Documentation](#documentation)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Quick Start](#quick-start)
- [Attribution](#attribution)
- [For Developers](#for-developers)

## Overview

**MITE** (Minimum Information about a Tailoring Enzyme) is a community-driven database for the characterization of tailoring enzymes.
These enzymes play crucial roles in the biosynthesis of secondary or specialized metabolites, naturally occurring molecules with strong biological activities, such as antibiotic properties.

This repository contains the **single source of truth** of the Minimum Information about a Tailoring Enzyme (MITE) database.

For more information, visit the [MITE Data Standard Organization page](https://github.com/mite-standard) or read our [publication]( https://doi.org/10.1093/nar/gkaf969).

## Documentation

This repository contains the **single source of truth** of the Minimum Information about a Tailoring Enzyme (MITE) database.

This data is in the form of JSON files controlled by [mite_schema](http://github.com/mite-standard/mite_schema) and validated by [mite_extras](https://github.com/mite-standard/mite_extras).
These files are created by user submissions via the [MITE web portal](https://mite.bioinformatics.nl/), expert-reviewed via pull requests, and then deposited in the [Zenodo](https://doi.org/10.5281/zenodo.13294303) repository.
From there, the [MITE web portal](https://mite.bioinformatics.nl/) and other tools such as antiSMASH pull the data for their own use.

This repository also provides some CLI functionality to generate auxiliary files:
- Metadata files summarizing information of all MITE entries in a single file (`mite_data/metadata`)
- Protein FASTA-files for all active (i.e. non-retired) MITE entries (`mite_data/fasta`)

For feature requests and suggestions, please refer to the [MITE Discussion forum](https://github.com/orgs/mite-standard/discussions/).

For simple data submissions, please refer to the [MITE web portal](https://mite.bioinformatics.nl/). For more complex or large-scale submission, please get in touch with us by e.g. opening an [Issue](http://github.com/mite-standard/mite_data/issues).

## System Requirements

### OS Requirements

Local installation was tested on:

- Ubuntu Linux 20.04 and 22.04 (command line)

#### Python dependencies

Dependencies including exact versions are specified in the [pyproject.toml](./pyproject.toml) file.

## Installation Guide

### With `uv` from GitHub

*Note: assumes that `uv` is installed locally - see the methods described [here](https://docs.astral.sh/uv/getting-started/installation/)*

```commandline
git clone https://github.com/mite-standard/mite_data
uv sync
```

## Quick Start

To update the auxiliary files, run:

- `uv run python ./mite_data/main.py`

To validate a single MITE file, run:

- `uv run python .github/mite_validation.py <your-mite-file>.json`

To validate all existing MITE files, run:

- `uv run python .github/mite_validation.py `

## Attribution

### License

All code and data in `mite_data` is released to the public domain under the CC0 license (see [LICENSE](LICENSE)).

### Publications

See [CITATION.cff](CITATION.cff) or [MITE online](https://mite.bioinformatics.nl/) for information on citing MITE.

### Acknowledgements

This work was supported by the Netherlands Organization for Scientific Research (NWO) KIC grant KICH1.LWV04.21.013.

## For Developers

*Nota bene: for details on how to contribute to the MITE project, please refer to [CONTRIBUTING](CONTRIBUTING.md).*

#### With `uv` from GitHub

*Note: assumes that `uv` is installed locally - see the methods described [here](https://docs.astral.sh/uv/getting-started/installation/)* 

```commandline
git clone https://github.com/mite-standard/mite_data
uv sync
uv run pre-commit install
```

All tests should be passing
```commandline
uv run pytest
```

### Updating and CI/CD

*Nota bene:* All described procedures require `pre-commit` to be installed and initiated .

CI/CD via GitHub Actions runs on every PR and push to the `main` branch.

A new release created on the [mite_data](https://github.com/mite-standard/mite_data) GitHub page will automatically relay changes to [Zenodo](https://doi.org/10.5281/zenodo.13294303).

### Update procedure

1. Merge reviewed pending pull requests (PRs) into main.
   - Fetch changes with `git fetch`.
   - Checkout remote branch with `git checkout -b local-<branch-uuid> origin/<branch-uuid>`.
   - Replace content of file `mite_data/data/<uuid>.json` with reviewed content from PR on GitHub.
   - Replace `status:pending` with `status:active` and coin a new MITE accession number. Check for any [reserved accessions](reserved_accessions.json).
   - Prepare a commit by running `git add . && git commit -m "reviewed entry"`
   - Push to remote with `git push origin HEAD:<branch-uuid>`
   - On GitHub, merge the respective PR into main and delete the feature branch.
   - Locally, checkout the main branch, pull in changes, and remove the local feature branch with `git checkout main && git pull && git branch -d local-<branch-uuid>`
   - Repeat for all open PRs on GitHub
2. Create a release branch and update auxilliary files
   - Fetch changes with `git fetch`.
   - Create a local branch and push to remote with `git checkout -b <release>`
   - Update version in `pyproject.toml` and `CHANGELOG.md`
   - Sync the package version with `uv sync`
   - Update metadata and add fasta files with `uv run python ./mite_data/main.py && uv run python .github/mite_validation.py`
   - Push to remote using `git push --set-upstream origin <release>`
3. Create PR on GitHub
   - Request a review (if applicable)
   - Merge into main
   - When all tests pass: create a new release (syncs data to Zenodo)

### CI/CD

`mite_data` employs automated checks using both `pre-commit` and CI/CD using GitHub Actions. 

## `pre-commit`

*Nota bene*: `pre-commit` applies checks only to new/modified files. 

#### Summary of checks

- `ruff` checks and linting
- `mite-validate`: runs `.github/mite_validation.py/run_file()`
- `pytest`: runs pytest

## GitHub CI/CD

### On PR to main

*Nota bene:* Applies checks only to new/modified files. 

#### Summary of checks

Runs `.github/mite_validation.py/run_file()`:

- File exists
- Filename matches convention
- File is release-ready (correct status, accession not one of [reserved](reserved_accessions.json))
- No duplicates (based on shared GenPept and UniProt IDs)
- Validation checks of `mite_extras` pass

### On push to main

*Nota bene:* Applies checks to all files (i.e. when a branch is merged into main). 

#### Summary of checks

Runs `.github/mite_validation.py/run_data_dir()`:

- File exists
- Filename matches convention
- File has an accompanying fasta file
- Retired files have no accompanying fasta files
- File is release-ready (correct status, accession not one of [reserved](reserved_accessions.json))
- No duplicates (based on shared GenPept and UniProt IDs)
- Validation checks of `mite_extras` pass

Additional checks:

- Package can be installed
- All tests passing
