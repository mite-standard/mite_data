# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [1.2] 15-10-2024

### Changed

- Updated entries to adhere to MITE schema version `1.4`
- All entries now pass automated checks of `mite_extras`
- Added the "Automated checks passed" reviewer ID `BBBBBBBBBBBBBBBBBBBBBBBB`
- Set the status of all entries to `active`
- Merged duplicate entries and retired them
- Reworked project structure
- complete rework of `mite_data` CLI
- added functionality to automatically generate metadata for MITE entries
- added functionality to download protein FASTA files and build a BLAST DB
- added functionality to update MITE entries to the newest version of `mite_schema`
- added a CI/CD pipeline to auto-check MITE entries at every commit

## [1.1] 11-08-2024

### Changed

- Updated entries to adhere to MITE schema version `1.3`

## [1.0] 30-07-2024

### Added

- Initial data upload
- Implementation of auxiliary scripts
