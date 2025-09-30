mite_extras
=========

[![DOI](https://zenodo.org/badge/834042284.svg)](https://zenodo.org/doi/10.5281/zenodo.13294303)

Contents
-----------------
- [Overview](#overview)
- [Documentation](#documentation)
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

1. Merge reviewed pending pull requests (PRs) into main
   - Fetch changes with `git fetch`
   - Checkout remote branch with `git checkout -b`
   - TBA
2. Create a release branch and update auxilliary files
   - TBA
   - Update version in `pyproject.toml` and`CHANGELOG.md`
   - Sync the package version with `uv sync`
   - On committing, `pre-commit` should automatically update the metadata and fasta files. If not, run `uv run python ./mite_data/main.py && uv run python .github/mite_validation.py`
3. Create a PR for the release branch


### CI/CD

TBA