# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.23] UNRELEASED

### Added

- Hash-based validation of artifacts

### Changed

- Separation of data and code
- Rework of validation functionality
- Rework of artifact creation/updating functionality
- Rework CI/CD logic
- Rework of pre-commit logic

### Removed

- pickle-file generation (fingerprint generation in mite_web on startup instead)

## [1.22] 14-01-2026

### Added

- Data update 01/26

### Changed

- Update pre-commit (change back)

## [1.21] 19-12-2025

### Added

- Data update 12/25

## [1.20] 07-12-2025

### Added

- Checks for MIBiG and Rhea IDs (implemented as warnings in mite_validation)
- Timeout for UniProt using requests
- Timeout for NCBI using concurrent.futures (Biopython Entrez lacks timeout, requests blocked by NCBI servers)
- Data update 11/25

### Fixed

- CI/CD run for new entries
- Fixed NCBI/Uniprot organism checks
- Prevent FASTA file download of retired entries

## [1.19] 27-10-2025

### Added

- Checks for validity of uniprot/genpept/wikidata
- Generation of molecule files for mite_web
- Added new entries

### Changed

- Fixed retired uniprot IDs


## [1.18] 30-09-2025

### Changed

- Changed installer from `hatch` to `uv`
- Updated dependencies & fixed tests to accommodate changes in Biopython's download from NCBI
- Reworked update procedure

### Added

- Data update

## [1.17] 26-08-2025

### Changed

- Miscellaneous fixes in context of manuscript revision
- MITE dependencies (`mite_schema`, `mite_extras`) resolve to most up-to-date version
- Implemented `uv` as project installer

## [1.16] 05-08-2025

### Changed

- Implemented additional tests for metadata_mibig.json file

## [1.15] 26-07-2025

### Changed

- Adjusted versions of `mite_extas` and `mite_schema`

## [1.14] 25-07-2025

### Added

- 06-25 data update
- added cofactor info

### Changed

- CI/CD: full check only on merge to main
- CI/CD: pull requests into main only check updated files

## [1.13] 02-06-2025

### Added

- 03/04/05-25 data update

## [1.12] 02-03-2025

### Added

- 02-25 data update

### Changed

- Changed collaboration documents to organization-level ones

## [1.11] 13-02-2025

### Changed

- Fixed format of CFF file

## [1.10] 13-02-2025

### Added

- Added entries for 01-25 data update

### Changed

- Changed the license from "MIT" to "CC0" where applicable

## [1.9] 02-01-2025

### Added

- Added entries for 12-24 data update
- Automated fasta-file download via pre-commit

### Changed

- Moved BLAST-library, .pdb-files, and enzyme visualizations to `mite_web`

## [1.8] 08-12-2024

### Bugfix

- Fixed error in BLAST library creation

## [1.7] 07-12-2024

### Added

- Completed review of all contained MITE entries

## [1.6] 30-11-2024

### Bugfix

- Fixed two entries with erroneous MITE ID

## [1.5] 30-11-2024

### Added

- Update data: November-release `1.5`
- Added "metadata_cytoscape.csv" to provide metadata for sequence similarity networks (fasta-files)

### Changed

- Pinned `mite_schema` and `mite_data` dependencies
- Replaced old IDs with ORCIDs
- Update metadata_mibig.json: changed nesting to accommodate multiple mite entries per mibig bgc

## [1.4] 09-11-2024

### Changed

- Updated entries to adhere to MITE schema version `1.5.1`

## [1.3] 21-10-2024

### Changed

- FASTA files are now named after the MITE entry they describe
- The header of FASTA file now contains `>{MITE accession} {genpept_id/uniprotkb_id/uniparc_id}` to keep track from where it originates

## [1.2] 19-10-2024

### Changed

- Updated entries to adhere to MITE schema version `1.4`
- All entries now pass automated checks of `mite_extras`
- Added the "Automated checks passed" reviewer ID `BBBBBBBBBBBBBBBBBBBBBBBB`
- Set the status of all entries to `active`
- Merged duplicate entries and retired them
- Reworked project structure
- Complete rework of `mite_data` CLI
- Added functionality to automatically generate metadata for MITE entries
- Added functionality to download protein FASTA files and build a BLAST DB
- Added functionality to update MITE entries to the newest version of `mite_schema`
- Added a CI/CD pipeline to auto-check MITE entries at every commit

## [1.1] 11-08-2024

### Changed

- Updated entries to adhere to MITE schema version `1.3`

## [1.0] 30-07-2024

### Added

- Initial data upload
- Implementation of auxiliary scripts
