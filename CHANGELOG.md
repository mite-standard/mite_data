# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.13] UNRELEASED

### Added

- 03/04/05-25 data update

## [1.12] 02-03-25

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
