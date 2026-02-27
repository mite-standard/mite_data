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
These enzymes play crucial roles in the biosynthesis of secondary or specialized metabolites.
These naturally occurring molecules often show strong biological activities, and many drugs (e.g. antibiotics) derive from them.

This repository contains the **single source of truth** of the Minimum Information about a Tailoring Enzyme (MITE) database.

For more information, visit the [MITE Data Standard Organization page](https://github.com/mite-standard) or read our [publication]( https://doi.org/10.1093/nar/gkaf969).

For feature requests and suggestions, please refer to the [MITE Discussion forum](https://github.com/orgs/mite-standard/discussions/).

For simple data submissions, please refer to the [MITE web portal](https://mite.bioinformatics.nl/). 
For more complex or large-scale submission, please get in touch with us by e.g. opening an [Issue](http://github.com/mite-standard/mite_data/issues).

### MITE Accession Reservation

You can reserve MITE Accession IDs for your to-be-published manuscript. Please read more about it in [this discussion](https://github.com/orgs/mite-standard/discussions/7).

## Documentation

This repository contains the **single source of truth** of the MITE database, as well as derived data artifacts.

This data is in the form of JSON files controlled by [mite_schema](http://github.com/mite-standard/mite_schema) 
These files are created by user submissions via the [MITE web portal](https://mite.bioinformatics.nl/).
Upon submission, entries are automatically checked with [mite_extras](https://github.com/mite-standard/mite_extras) library and a new pull request is created.

After user submission, our domain expert reviewers check then entries and approve the pull requests.
Next, automatic checks are performed to check entries and automatically create the derived artifacts.

Upon release of a new version, data is automatically backed up in its [Zenodo](https://doi.org/10.5281/zenodo.13294303) repository, from where it is used by other sources (e.g. [MITE Web](https://mite.bioinformatics.nl/))


## Attribution

### License

All code and data in `mite_data` is released to the public domain under the CC0 license (see [LICENSE](LICENSE)).

### Publications

See [CITATION.cff](CITATION.cff) or [MITE online](https://mite.bioinformatics.nl/) for information on citing MITE.

### Acknowledgements

This work was supported by the Netherlands Organization for Scientific Research (NWO) KIC grant KICH1.LWV04.21.013.

## For Developers

### Release checklist

Workflow for release creation (for details, see below):

- Update version in [pyproject.toml](pyproject.toml) file (major is reserved to manuscript publications)
- On [new release](https://github.com/mite-standard/mite_data/releases/new), fill in tag (`version`, prefixed with `v`), add `version` as release title, and add release notes (identical to `changelog`)
- **IMPORTANT: SAVE AS DRAFT** - this will automatically trigger the release workflow that also performs the CI/CD checks
- **DO NOT PUBLISH RELEASE MANUALLY**


### Background


The repo consists of a data part (`mite_data`) and an associated validation library (`mite_data_lib`).

A number of pipelines is available to perform fully automated data validation and artifact validation and generation.

Additionally, a [json file](reserved/reserved_accessions.json) allows to track reserved MITE accessions.

```
repo/
├ mite_data/      <-- source of truth
|     ├ data/     <-- MITE JSON entries
|     ├ fasta/    <-- FASTA files related to MITE entries
|     ├ metadata/ <-- Artifacts created from MITE entries
|     └ mibig/    <-- Artifacts created from MIBiG dataset 
├ reserved/       <-- Reserved MITE accessions
├ mite_data_lib/  <-- Validation library
|     ├ config/   <-- Library-wide configuration settings
|     ├ models/   <-- (Pydantic) data contracts
|     ├ rules/    <-- Validation rules
|     └ services/ <-- Artifact generation
└ pipeline/       <-- Data processing pipelines

```

#### CI/CD


To preserve data integrity, this repository implements several stages of CI/CD (continuous integration/continuous deployment) using GitHub Actions.
These actions are tiggered automatically and perform validation and artifact generation in a stepwise manner, as described below.

```
Pull request (affecting mite_data/data)   <-- User contribution
├ pipeline/validate_mibig.py              <-- Reference dataset validation
├ pipeline/validate_entry.py              <-- MITE entry validation
Commit to main (affecting mite_data/data) <-- PR merge by maintainer
├ pipeline/create_artifacts.py            <-- Artifact creation
New release                               <-- By maintainer
└ pipeline/validate_artifacts.py          <-- Validate artifacts + entries
```

Every PR affecting the `mite_data/data` directory automatically triggers data validation functions.
Only if these pass, the PR may be merged into main.

Every commit to main affecting the `mite_data/data` directory automatically triggers artifact creation.
These artifacts are automatically added to main to reflect the updated file.

Every new release triggers the artifact and entry validation pipeline.
This step is computationally expensive but provides a sanity check.

If the MIBiG validation check does not pass, the MIBiG dataset needs to be updated manually (see below)

### Manual execution/development

For development purposes, pipelines can also be run automatically. For this, local installation is required, as follows:

*Nota bene: local installation was only tested on Ubuntu Linux 20.04 and 22.04. Also assumes that `uv` is installed locally - see the methods described [here](https://docs.astral.sh/uv/getting-started/installation/)*

1) Download and install

```commandline
git clone https://github.com/mite-standard/mite_data
uv sync
uv run pre-commit install
```
2) Run tests

```commandline
uv run pytest --download # includes more time-consuming tests with network calls
```

3) Run pipelines

```commandline
uv run python pipeline/validate_mibig.py                          # Checks if MIBIG Ref is valid
uv run python pipeline/create_mibig.py                            # Downloads MIBiG Ref dataset
uv run python pipeline/validate_entry.py entry1.json ...          # Checks entries
uv run python pipeline/create_artifacts_single.py entry1.json ... # Creates artifacts in single entry mode
uv run python pipeline/create_artifacts_all.py                    # Re-creates all artifacts (expensive!)
uv run python validate_artifacts.py                               # Validates artifacts
```

#### Adding new rules

All rules follow a standardized API.

- Add your rule to [rules](mite_data_lib/rules). Follow the interface of the existing functions.
- Update the corresponding [pipeline](pipeline)