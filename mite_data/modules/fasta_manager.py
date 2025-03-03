"""Manages fasta file download.

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
import logging
from pathlib import Path
from typing import Self

import requests
from Bio import Entrez
from pydantic import BaseModel, DirectoryPath, FilePath

logger = logging.getLogger("mite_data")
Entrez.email = "your_email@example.com"  # must be set but does not have to be real


class FastaManager(BaseModel):
    """Manages the download of FASTA files.

    Not all MITE entries have NCBI GenPept accessions - some only have UniProt IDs.

    The manager first extracts accessions - MITE file does not have a GenPept ID, it will take
    the UniProtKB or UniParc ID.

    Attributes:
        genpept_acc: a list of uniprot accession IDs for download
        uniprot_acc: a list of uniprot accession IDs for download
        src: a Path towards the metadata source file
        target_download: a Path towards the fasta file target (storage) directory
    """

    genpept_acc: list = []
    uniprot_acc: list = []
    src: FilePath = Path(__file__).parent.parent.joinpath(
        "metadata/metadata_general.json"
    )
    target_download: DirectoryPath = Path(__file__).parent.parent.joinpath("fasta/")

    def run(self: Self) -> None:
        """Class entry point to run methods

        Raises:
            RuntimeError: New fasta files were downloaded (needed to abort pre-commit)

        """
        logger.info("Started FastaManager.")
        nr_files_pre = len(list(Path(self.target_download).glob("*")))
        try:
            self.extract_accessions()
            self.download_ncbi()
            self.download_uniprot()

            nr_files_post = len(list(Path(self.target_download).glob("*")))
            if nr_files_pre != nr_files_post:
                raise RuntimeError(
                    "Fasta files were downloaded - add them to version control."
                )

        except Exception as e:
            logger.error(f"An error has occurred: {e!s}")
            raise e

        logger.info("Completed FastaManager.")

    def extract_accessions(self: Self) -> None:
        """Extracts NCBI GenPept and UniProt accession IDs from metadata file.

        Raises:
            RuntimeError: An entry does not have a GenPept or UniProt accession ID.
        """
        with open(self.src) as file_in:
            metadata_general = json.load(file_in)
        for entry in metadata_general["entries"]:
            if metadata_general["entries"][entry]["status"] != "active":
                logger.debug(
                    f"FastaManager: MITE entry {entry} has been retired and will not be downloaded as fasta file."
                )
                continue
            elif acc := metadata_general["entries"][entry]["enzyme_ids"].get(
                "genpept", None
            ):
                self.genpept_acc.append({"entry": entry, "acc": acc})
            elif acc := metadata_general["entries"][entry]["enzyme_ids"].get(
                "uniprot", None
            ):
                self.uniprot_acc.append({"entry": entry, "acc": acc})
            else:
                raise RuntimeError(f"{entry} has no GenPept or UniProt ID - FIX ASAP!")

    def download_ncbi(self: Self) -> None:
        """Download protein FASTA files from NCBI GenPept, skip already existing files."""
        if len(self.genpept_acc) == 0:
            logger.warning(
                f"No fasta-files scheduled to be downloaded from NCBI - SKIP"
            )
            return

        for entry in self.genpept_acc:
            if self.target_download.joinpath(f"{entry["entry"]}.fasta").exists():
                logger.debug(
                    f"File '{self.target_download.joinpath(f"{entry["entry"]}.fasta")}' already exists - SKIP"
                )
                continue

            handle = Entrez.efetch(
                db="protein", id=entry["acc"], rettype="fasta", retmode="text"
            )
            fasta_data = handle.read()
            handle.close()

            lines = fasta_data.strip().split("\n")
            if lines:
                lines[0] = f">{entry["entry"]} {entry["acc"]}"
            fasta_data = "\n".join(lines)

            with open(
                self.target_download.joinpath(f"{entry["entry"]}.fasta"), "w"
            ) as fasta_file:
                fasta_file.write(fasta_data)

    def download_uniprot(self: Self) -> None:
        """Download protein FASTA files from UniProt

        Raises:
            RuntimeError: Could not download UniProt data
        """

        def _store_file(data: dict, lines: list) -> None:
            if lines:
                lines[0] = f">{data["entry"]} {data["acc"]}"
            else:
                raise RuntimeError(
                    f"UniProt download failed on ID {data["acc"]} for MITE entry {data["entry"]}"
                )
            payload = "\n".join(lines)
            with open(
                self.target_download.joinpath(f"{data["entry"]}.fasta"), "w"
            ) as fasta_file:
                fasta_file.write(payload)

        if len(self.uniprot_acc) == 0:
            logger.warning(
                f"No fasta-files scheduled to be downloaded from UniProt - SKIP"
            )
            return

        for entry in self.uniprot_acc:
            if self.target_download.joinpath(f"{entry["entry"]}.fasta").exists():
                logger.debug(
                    f"File '{self.target_download.joinpath(f"{entry["entry"]}.fasta")}' already exists - SKIP"
                )
                continue

            if (
                response := requests.get(
                    f"https://rest.uniprot.org/uniprotkb/{entry["acc"]}.fasta"
                )
            ).status_code == 200 or (
                response := requests.get(
                    f"https://rest.uniprot.org/uniparc/{entry["acc"]}.fasta"
                )
            ).status_code == 200:
                _store_file(data=entry, lines=response.text.strip().split("\n"))
            else:
                raise RuntimeError(
                    f"UniProt download failed on ID {entry["acc"]} for MITE entry {entry["entry"]}"
                )
