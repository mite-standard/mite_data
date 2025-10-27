"""MITE validation CI/CD pipeline, to be used with pre-commit.

Creative Commons Legal Code

CC0 1.0 Universal

    CREATIVE COMMONS CORPORATION IS NOT A LAW FIRM AND DOES NOT PROVIDE
    LEGAL SERVICES. DISTRIBUTION OF THIS DOCUMENT DOES NOT CREATE AN
    ATTORNEY-CLIENT RELATIONSHIP. CREATIVE COMMONS PROVIDES THIS
    INFORMATION ON AN "AS-IS" BASIS. CREATIVE COMMONS MAKES NO WARRANTIES
    REGARDING THE USE OF THIS DOCUMENT OR THE INFORMATION OR WORKS
    PROVIDED HEREUNDER, AND DISCLAIMS LIABILITY FOR DAMAGES RESULTING FROM
    THE USE OF THIS DOCUMENT OR THE INFORMATION OR WORKS PROVIDED
    HEREUNDER.

Statement of Purpose

The laws of most jurisdictions throughout the world automatically confer
exclusive Copyright and Related Rights (defined below) upon the creator
and subsequent owner(s) (each and all, an "owner") of an original work of
authorship and/or a database (each, a "Work").

Certain owners wish to permanently relinquish those rights to a Work for
the purpose of contributing to a commons of creative, cultural and
scientific works ("Commons") that the public can reliably and without fear
of later claims of infringement build upon, modify, incorporate in other
works, reuse and redistribute as freely as possible in any form whatsoever
and for any purposes, including without limitation commercial purposes.
These owners may contribute to the Commons to promote the ideal of a free
culture and the further production of creative, cultural and scientific
works, or to gain reputation or greater distribution for their Work in
part through the use and efforts of others.

For these and/or other purposes and motivations, and without any
expectation of additional consideration or compensation, the person
associating CC0 with a Work (the "Affirmer"), to the extent that he or she
is an owner of Copyright and Related Rights in the Work, voluntarily
elects to apply CC0 to the Work and publicly distribute the Work under its
terms, with knowledge of his or her Copyright and Related Rights in the
Work and the meaning and intended legal effect of CC0 on those rights.

1. Copyright and Related Rights. A Work made available under CC0 may be
protected by copyright and related or neighboring rights ("Copyright and
Related Rights"). Copyright and Related Rights include, but are not
limited to, the following:

  i. the right to reproduce, adapt, distribute, perform, display,
     communicate, and translate a Work;
 ii. moral rights retained by the original author(s) and/or performer(s);
iii. publicity and privacy rights pertaining to a person's image or
     likeness depicted in a Work;
 iv. rights protecting against unfair competition in regards to a Work,
     subject to the limitations in paragraph 4(a), below;
  v. rights protecting the extraction, dissemination, use and reuse of data
     in a Work;
 vi. database rights (such as those arising under Directive 96/9/EC of the
     European Parliament and of the Council of 11 March 1996 on the legal
     protection of databases, and under any national implementation
     thereof, including any amended or successor version of such
     directive); and
vii. other similar, equivalent or corresponding rights throughout the
     world based on applicable law or treaty, and any national
     implementations thereof.

2. Waiver. To the greatest extent permitted by, but not in contravention
of, applicable law, Affirmer hereby overtly, fully, permanently,
irrevocably and unconditionally waives, abandons, and surrenders all of
Affirmer's Copyright and Related Rights and associated claims and causes
of action, whether now known or unknown (including existing as well as
future claims and causes of action), in the Work (i) in all territories
worldwide, (ii) for the maximum duration provided by applicable law or
treaty (including future time extensions), (iii) in any current or future
medium and for any number of copies, and (iv) for any purpose whatsoever,
including without limitation commercial, advertising or promotional
purposes (the "Waiver"). Affirmer makes the Waiver for the benefit of each
member of the public at large and to the detriment of Affirmer's heirs and
successors, fully intending that such Waiver shall not be subject to
revocation, rescission, cancellation, termination, or any other legal or
equitable action to disrupt the quiet enjoyment of the Work by the public
as contemplated by Affirmer's express Statement of Purpose.

3. Public License Fallback. Should any part of the Waiver for any reason
be judged legally invalid or ineffective under applicable law, then the
Waiver shall be preserved to the maximum extent permitted taking into
account Affirmer's express Statement of Purpose. In addition, to the
extent the Waiver is so judged Affirmer hereby grants to each affected
person a royalty-free, non transferable, non sublicensable, non exclusive,
irrevocable and unconditional license to exercise Affirmer's Copyright and
Related Rights in the Work (i) in all territories worldwide, (ii) for the
maximum duration provided by applicable law or treaty (including future
time extensions), (iii) in any current or future medium and for any number
of copies, and (iv) for any purpose whatsoever, including without
limitation commercial, advertising or promotional purposes (the
"License"). The License shall be deemed effective as of the date CC0 was
applied by Affirmer to the Work. Should any part of the License for any
reason be judged legally invalid or ineffective under applicable law, such
partial invalidity or ineffectiveness shall not invalidate the remainder
of the License, and in such case Affirmer hereby affirms that he or she
will not (i) exercise any of his or her remaining Copyright and Related
Rights in the Work or (ii) assert any associated claims and causes of
action with respect to the Work, in either case contrary to Affirmer's
express Statement of Purpose.

4. Limitations and Disclaimers.

 a. No trademark or patent rights held by Affirmer are waived, abandoned,
    surrendered, licensed or otherwise affected by this document.
 b. Affirmer offers the Work as-is and makes no representations or
    warranties of any kind concerning the Work, express, implied,
    statutory or otherwise, including without limitation warranties of
    title, merchantability, fitness for a particular purpose, non
    infringement, or the absence of latent or other defects, accuracy, or
    the present or absence of errors, whether or not discoverable, all to
    the greatest extent permissible under applicable law.
 c. Affirmer disclaims responsibility for clearing rights of other persons
    that may apply to the Work or any use thereof, including without
    limitation any person's Copyright and Related Rights in the Work.
    Further, Affirmer disclaims responsibility for obtaining any necessary
    consents, permissions or other rights required for any use of the
    Work.
 d. Affirmer understands and acknowledges that Creative Commons is not a
    party to this document and has no duty or obligation with respect to
    this CC0 or use of the Work.
"""

import json
from pathlib import Path
from sys import argv
from typing import Self

from mite_extras import MiteParser
from mite_extras.processing.validation_manager import IdValidator
from mite_schema import SchemaManager
from pydantic import BaseModel, DirectoryPath, FilePath, model_validator

from mite_data.modules.fasta_manager import FastaManager


class CicdManager(BaseModel):
    """Manage methods to validate MITE entries in pre-commit and CI/CD

    Attributes:
        src: a Path towards the source directory
        fasta: a Path towards to directory containing accompanying fasta files
        reserved_path: Path to json file of reserved accessions
        issues: all issues detected during run
        genpept: a list of genbank accessions in mite_data
        uniprot: a list of uniprot accessions in mite_data
        reserved: a list of reserved accessions (mustn't be used)
    """

    src: DirectoryPath = Path(__file__).parent.parent.joinpath("data/")
    fasta: DirectoryPath = Path(__file__).parent.parent.joinpath("fasta/")
    reserved_path: FilePath = Path(__file__).parent.parent.joinpath(
        "reserved_accessions.json"
    )
    issues: list = []
    genpept: dict = {}
    uniprot: dict = {}
    reserved: list = []

    @model_validator(mode="after")
    def fill_accessions(self):
        """Pull out all accession files"""
        for entry in self.src.iterdir():
            with open(entry) as infile:
                data = json.load(infile)
            if data["status"] != "active":
                continue

            if acc := data["enzyme"]["databaseIds"].get("genpept", None):
                if acc in self.genpept:
                    self.genpept[acc].append(data["accession"])
                else:
                    self.genpept[acc] = [data["accession"]]

            if acc := data["enzyme"]["databaseIds"].get("uniprot", None):
                if acc in self.uniprot:
                    self.uniprot[acc].append(data["accession"])
                else:
                    self.uniprot[acc] = [data["accession"]]
        return self

    @model_validator(mode="after")
    def get_reserved(self):
        with open(self.reserved_path) as infile:
            data = json.load(infile)
        if data.get("reserved"):
            self.reserved = [i[0] for i in data.get("reserved")]
        return self

    def run_file(self: Self, path: str) -> None:
        """Run a single file against validation functions

        Used by GitHub Actions ci_pr_main.yml and pre-commit

        Arguments:
            path: a file path

        Raises:
            FileNotFoundError: mite file or mite fasta file not found
            RuntimeError: one or more issues with files detected
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Could not find file '{path}'")

        if not path.name.startswith("MITE"):
            return

        self.check_file_naming(path)

        with open(path) as infile:
            data = json.load(infile)

        self.check_release_ready(data=data)
        self.check_duplicates(data=data)
        self.validate_entries_passing(data=data)
        self.validate_db_ids(data=data)

        if len(self.issues) != 0:
            raise RuntimeError("\n".join(self.issues))

    def run_data_dir(self: Self) -> None:
        """Run all files against validation functions

        Used by GitHub Actions ci_push_main.yml

        Raises:
            FileNotFoundError: mite file not found
            RuntimeError: one or more issues with files detected
        """
        for path in self.src.iterdir():
            if not path.exists():
                raise FileNotFoundError(f"Could not find file '{path}'")

            self.check_file_naming(path)

            with open(path) as infile:
                data = json.load(infile)
            if data["status"] != "active":
                if self.fasta.joinpath(f"{path.stem}.fasta").exists():
                    self.issues.append(
                        f"File '{path.name}' is not active but still has an accompanying fasta file - remove it. \n"
                        f"{self.fasta.joinpath(f'{path.stem}.fasta')}"
                    )
                continue

            if not self.fasta.joinpath(f"{path.stem}.fasta").exists():
                self.issues.append(
                    f"File '{path.name}' does not have an accompanying fasta file."
                )

            self.check_release_ready(data=data)
            self.check_duplicates(data=data)
            self.check_fasta_header(data=data)
            self.validate_entries_passing(data=data)
            self.validate_db_ids(data=data)

        if len(self.issues) != 0:
            raise RuntimeError("\n".join(self.issues))

    def check_file_naming(self: Self, path: Path) -> None:
        """Check if follows naming

        Args:
            path: a Path object pointing to file
        """
        if not path.name.startswith("MITE") or path.suffix != ".json":
            self.issues.append(
                f"File '{path.name}' does not follow naming convention 'MITEnnnnnnn.json'."
            )

    def check_release_ready(self: Self, data: dict) -> None:
        """Verify that entry does not have the status tag 'pending' or the MITE ID MITE9999999

        Argument:
            data: the mite entry data
        """
        if data["status"] == "pending":
            self.issues.append(
                f"Entry '{data["accession"]}' has the status flag 'pending'. This must be set to 'active' before release."
            )

        if data["accession"] in self.reserved:
            self.issues.append(
                f"The MITE accession '{data["accession"]}' is already reserved. Please change this to another accession number."
            )

    def check_duplicates(self: Self, data: dict) -> None:
        """Check if multiple MITE entries describe the same enzyme using GenPept/UniProt IDs

        Argument:
            data: the mite entry data
        """
        if data["status"] != "active":
            return

        if acc := data["enzyme"]["databaseIds"].get("genpept", None):
            if len(self.genpept[acc]) > 1:
                self.issues.append(
                    f"Multiple entries share the same GenPept ID '{acc}': '{self.genpept[acc]}'"
                )

        if acc := data["enzyme"]["databaseIds"].get("uniprot", None):
            if len(self.uniprot[acc]) > 1:
                self.issues.append(
                    f"Multiple entries share the same UniProt ID '{acc}': '{self.uniprot[acc]}'"
                )

    def check_fasta_header(self: Self, data: dict) -> None:
        """Check if MITE file and corresponding FASTA file share headers

        Argument:
            data: the mite entry data
        """
        fasta = self.fasta.joinpath(f"{data["accession"]}.fasta")
        if not fasta.exists():
            self.issues.append(
                f"File {fasta.name} expected but missing. Must be added before release!"
            )
            return

        with open(fasta) as infile:
            lines = infile.read()

        accession = lines.split()[1]
        ids = [
            data["enzyme"]["databaseIds"].get(i, None) for i in ("genpept", "uniprot")
        ]

        if not accession in ids:
            self.issues.append(
                f"{data["accession"]}: database IDs '{ids}' do not match accession in {data["accession"]}.fasta '{accession}'. \n"
                "Please check if the IDs were updated but the fasta file not."
            )

    def validate_entries_passing(self: Self, data: dict) -> None:
        """Check if MITE entries pass automated validation checks of mite_extras

        Argument:
            data: the mite entry data
        """
        try:
            parser = MiteParser()
            parser.parse_mite_json(data=data)
            schema_manager = SchemaManager()
            schema_manager.validate_mite(instance=parser.to_json())
        except Exception as e:
            self.issues.append(
                f"Error: entry {data["accession"]} failed validation ({e})."
            )

    def validate_db_ids(self: Self, data: dict) -> None:
        """Check if MITE entry IDs all pass checks

        Argument:
            data: the mite entry data
        """
        id_val = IdValidator()
        fasta_mngr = FastaManager()

        try:
            ncbi = data["enzyme"]["databaseIds"].get("genpept", None)
            if ncbi:
                fasta_mngr.download_ncbi(mite_acc=data["accession"], genpept_acc=ncbi)

            uniprot = data["enzyme"]["databaseIds"].get("uniprot", None)
            if uniprot:
                fasta_mngr.download_uniprot(
                    mite_acc=data["accession"], uniprot_acc=uniprot
                )

            if data["enzyme"]["databaseIds"].get("wikidata", None):
                id_val.validate_wikidata_qid(
                    qid=data["enzyme"]["databaseIds"]["wikidata"]
                )
        except Exception as e:
            self.issues.append(
                f"Error: entry {data["accession"]} failed validation of DB crosslinks ({e})."
            )


if __name__ == "__main__":
    manager = CicdManager()

    try:
        manager.run_file(path=argv[1])
    except IndexError:
        manager.run_data_dir()
