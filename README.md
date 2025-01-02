# Overview

[![DOI](https://zenodo.org/badge/834042284.svg)](https://zenodo.org/doi/10.5281/zenodo.13294303)

This repository contains the **"ground truth"** dataset of the Minimum Information about a Tailoring Enzyme (MITE) data repository (`mite_data/data`).

Furthermore, the repository contains auxiliary files and scripts to automatically update them:

- Metadata files summarizing information of all MITE entries in a single file (`mite_data/metadata`)
- Protein FASTA-files for all active (i.e. non-retired) MITE entries (`mite_data/fasta`)

For more information on MITE, see the README of the [MITE-Standard organisation page](https://github.com/mite-standard).

## For developers

*Nota bene*: This installation will only work on (Ubuntu) Linux.

- Install `python 3.12.x`
- Install hatch (e.g. with `pipx install hatch`)
- `hatch env create`
- Update metadata files and download fasta files: `mite_data`
