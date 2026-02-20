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


# TODO: remove file

import json
from pathlib import Path
from sys import argv
from typing import Self

import requests
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
        mibig: Path towards mibig proteins file
        mibig_proteins: dict of MIBiG IDs and corresponding genpepts
        reserved_path: Path to json file of reserved accessions
        errors: all errors detected during run
        warnings: all warnings (do not raise errors)
        genpept: a list of genbank accessions in mite_data
        uniprot: a list of uniprot accessions in mite_data
        reserved: a list of reserved accessions (mustn't be used)
    """

    src: DirectoryPath = Path(__file__).parent.parent.joinpath("data/")
    fasta: DirectoryPath = Path(__file__).parent.parent.joinpath("fasta/")
    mibig: FilePath = Path(__file__).parent.parent.joinpath("mibig/mibig_proteins.json")
    mibig_proteins: dict = {}
    reserved_path: FilePath = Path(__file__).parent.parent.joinpath(
        "reserved_accessions.json"
    )
    errors: list = []
    warnings: list = []
    genpept: dict = {}
    uniprot: dict = {}
    reserved: list = []

    def check_fasta_header(self: Self, data: dict) -> None:
        """Check if MITE file and corresponding FASTA file share headers

        Argument:
            data: the mite entry data
        """
        fasta = self.fasta.joinpath(f"{data["accession"]}.fasta")
        if not fasta.exists():
            self.errors.append(
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
            self.errors.append(
                f"{data["accession"]}: database IDs '{ids}' do not match accession in {data["accession"]}.fasta '{accession}'. \n"
                "Please check if the IDs were updated but the fasta file not."
            )

    def validate_db_ids(self: Self, data: dict) -> None:
        """Check if MITE cross-reference IDs can be accessed (=downloaded)

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
            self.errors.append(
                f"Error: entry {data["accession"]} failed validation of DB crosslinks ({e})."
            )

    def check_match_db_ids(self: Self, data: dict) -> None:
        """Check if uniprot and genpept IDs correspond to each other

        Does currently not work for UniParc - cross-check omitted.

        Argument:
            data: the mite entry data
        """
        id_val = IdValidator()

        uniprot = data["enzyme"]["databaseIds"].get("uniprot", None)
        genpept = data["enzyme"]["databaseIds"].get("genpept", None)

        if uniprot and uniprot.startswith("UPI"):
            return

        try:
            if uniprot and genpept:
                id_val.cleanup_ids(genpept=genpept, uniprot=uniprot)
            elif uniprot:
                match = id_val.cleanup_ids(uniprot=uniprot)
                self.warnings.append(
                    f"Warning: {data["accession"]}'s missing GenPept ID {match["genpept"]} can be automatically added using UniProt ID {uniprot}"
                )
            elif genpept:
                match = id_val.cleanup_ids(genpept=genpept)
                self.warnings.append(
                    f"Warning: {data["accession"]}'s missing UniProt ID {match["uniprot"]} can be automatically added using GenPept ID {genpept}"
                )
        except Exception as e:
            self.warnings.append(
                f"Warning: error during EnzymeDatabaseIds validation: {e!s}"
            )

    def check_mibig(self: Self, data: dict) -> None:
        """Check if genpept part of MIBiG if MIBiG ID was specified

        Argument:
            data: the mite entry data
        """
        mibig = data["enzyme"]["databaseIds"].get("mibig")
        genpept = data["enzyme"]["databaseIds"].get("genpept")

        if not mibig:
            return

        if not genpept:
            self.errors.append(
                f"Error: entry {data["accession"]} has MIBiG ID {mibig} but no GenPept ID: not allowed."
            )
            return

        if mibig not in self.mibig_proteins:
            self.warnings.append(
                f"Warning: entry {data["accession"]}'s MIBiG ID {mibig} not found in known MIBiG IDs, perhaps because it is retired. Double-check on MIBiG website if it really exists."
            )
            return

        if genpept not in self.mibig_proteins[mibig]:
            self.errors.append(
                f"Error: entry {data["accession"]}'s GenPept ID {genpept} is not found in the proteins of the referenced MIBiG ID {mibig}."
            )

    def check_rhea(self: Self, data: dict, timeout: float = 5.0) -> None:
        """Check if UniProt can be annotated with Rhea ID

        Argument:
            data: the mite entry data
        """
        uniprot = data["enzyme"]["databaseIds"].get("uniprot")
        if not uniprot:
            return

        known_rhea = set()
        for reaction in data["reactions"]:
            if val := reaction.get("databaseIds", {}).get("rhea"):
                known_rhea.add(val)
        try:
            response = requests.get(
                url="https://www.rhea-db.org/rhea?",
                params={
                    "query": uniprot,
                    "columns": "rhea-id",
                    "format": "tsv",
                    "limit": 10,
                },
                timeout=timeout,
            )
        except requests.exceptions.ConnectTimeout:
            self.warnings.append(f"Warning: could not connect to Rhea: Timeout")
            return

        retrieved_rhea = set()
        if response.status_code == 200:
            retrieved_rhea = {
                i.removeprefix("RHEA:") for i in response.text.split()[2:]
            }

        if known_rhea != retrieved_rhea:
            self.warnings.append(
                f"Warning: entry {data["accession"]} shows mismatch between annotated and retrieved RHEA IDs: \n"
                f"Annotated RHEA IDs: {sorted(known_rhea)} \n"
                f"Retrieved RHEA IDs: {sorted(retrieved_rhea)}"
            )


if __name__ == "__main__":
    manager = CicdManager()

    try:
        manager.run_file(path=argv[1])
    except IndexError:
        manager.run_data_dir()
