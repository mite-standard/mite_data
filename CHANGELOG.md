# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5] UNRELEASED

### Added

- Update data: December-release


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
