"""Metadata (update) manager.

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
from importlib import metadata
from pathlib import Path
from typing import Self

import pandas as pd
import requests
from Bio import Entrez, SeqIO
from pydantic import BaseModel, DirectoryPath, model_validator

logger = logging.getLogger("mite_data")


class MetadataManager(BaseModel):
    """Manage metadata collection from MITE entries.

    Attributes:
        src: MITE data dir path
        meta: metadata storeage path
        mibig: MIBiG data path
        mibig_data: pre-extracted BGC-protein mappings
    """

    src: DirectoryPath = Path(__file__).parent.parent.joinpath("data/")
    meta: DirectoryPath = Path(__file__).parent.parent.joinpath("metadata/")
    mibig: DirectoryPath = Path(__file__).parent.parent.joinpath("mibig/")
    mibig_data: dict = {}
    meta_gen: dict = {}
    meta_mibig: dict = {}

    @model_validator(mode="after")
    def populate_mibig_data(self):
        """Poputates mibig data

        Raises:
            ValueError: MIBiG directory not found
        """
        if not self.mibig.exists():
            raise ValueError(f"MIBiG data directory does not exist - ABORT")
        with open(self.mibig.joinpath("mibig_proteins.json")) as file_in:
            self.mibig_data = json.load(file_in)
        return self

    @model_validator(mode="after")
    def populate_metadata(self):
        """Poputates metadata if exists"""
        if self.meta.joinpath("metadata_general.json").exists():
            with open(self.meta.joinpath("metadata_general.json")) as fin:
                self.meta_gen = json.load(fin)
        else:
            self.meta_gen = {
                "version_mite_data": f"{metadata.version('mite_data')}",
                "entries": {},
            }

        if self.meta.joinpath("metadata_mibig.json").exists():
            with open(self.meta.joinpath("metadata_mibig.json")) as fin:
                self.meta_mibig = json.load(fin)
        else:
            self.meta_mibig = {
                "version_mite_data": f"{metadata.version('mite_data')}",
                "entries": {},
            }
        return self

    def update_single(self, path: Path) -> None:
        """Update metadata of a single file

        Arguments:
            path: a file path
        """
        logger.info(f"Started MetadataManager on file {path.name}.")

        data = self.load_json(path=path)
        self.extr_meta_gen(data=data)
        self.extr_meta_mibig(data=data)
        self.dump_json(
            path=self.meta.joinpath("metadata_general.json"), data=self.meta_gen
        )
        self.dump_json(
            path=self.meta.joinpath("metadata_mibig.json"), data=self.meta_mibig
        )
        self.dump_summary_csv()

        logger.info(f"Completed MetadataManager on file {path.name}.")

    def update_all(self) -> None:
        """Update metadata of all files (overwrite all)"""
        logger.info("Started MetadataManager on all files.")

        for path in self.src.iterdir():
            data = self.load_json(path=path)
            self.extr_meta_gen(data=data)
            self.extr_meta_mibig(data=data)

        self.dump_json(
            path=self.meta.joinpath("metadata_general.json"), data=self.meta_gen
        )
        self.dump_json(
            path=self.meta.joinpath("metadata_mibig.json"), data=self.meta_mibig
        )
        self.dump_summary_csv()

        logger.info("Completed MetadataManager on all files.")

    @staticmethod
    def load_json(path: Path) -> dict:
        """Load JSON-based data

        Returns:
            The loaded JSON as dict
        """
        with open(path) as fin:
            return json.load(fin)

    @staticmethod
    def dump_json(path: Path, data: dict) -> None:
        """Dump dict as JSON

        Params:
            path: the path to dump data to
            data: the data to dump
        """
        with open(path, "w", encoding="utf-8") as fout:
            fout.write(json.dumps(data, indent=2, ensure_ascii=False))

    def dump_summary_csv(self):
        """Dump summary in csv format for mite_web"""
        dump = {
            "accession": [],
            "status": [],
            "name": [],
            "tailoring": [],
            "cofactors_organic": [],
            "cofactors_inorganic": [],
            "description": [],
            "reaction_description": [],
            "organism": [],
            "domain": [],
            "kingdom": [],
            "phylum": [],
            "class": [],
            "order": [],
            "family": [],
        }

        keys = sorted(self.meta_gen["entries"].keys())
        summary = {"entries": {key: self.meta_gen["entries"][key] for key in keys}}

        for key, val in summary["entries"].items():
            dump["accession"].append(key)
            dump["status"].append(val["status"])
            dump["name"].append(val["enzyme_name"])
            dump["tailoring"].append(val["tailoring"])
            dump["cofactors_organic"].append(val["cofactors_organic"])
            dump["cofactors_inorganic"].append(val["cofactors_inorganic"])
            dump["description"].append(val["enzyme_description"])
            dump["reaction_description"].append(val["reaction_description"])
            dump["organism"].append(val["organism"])
            dump["domain"].append(val["domain"])
            dump["kingdom"].append(val["kingdom"])
            dump["phylum"].append(val["phylum"])
            dump["class"].append(val["class"])
            dump["order"].append(val["order"])
            dump["family"].append(val["family"])

        df = pd.DataFrame(dump)
        df.to_csv(self.meta.joinpath("summary.csv"), index=False)

    def extr_meta_gen(self, data: dict) -> None:
        """Extract metadata, store formatted for 'general'

        Params:
            data: the MITE json
        """
        origin = self.get_taxonomy(data)

        meta = {
            "accession": data["accession"],
            "status": data["status"],
            "status_icon": '<i class="bi bi-check-circle-fill"></i>'
            if data.get("status") == "active"
            else '<i class="bi bi-circle"></i>',
            "enzyme_name": data["enzyme"]["name"],
            "enzyme_description": data.get("enzyme", {}).get(
                "description", "No description available"
            ),
            "enzyme_ids": data["enzyme"]["databaseIds"],
            "tailoring": "|".join(
                sorted(
                    {
                        tailoring
                        for reaction in data.get("reactions")
                        for tailoring in reaction.get("tailoring", [])
                    }
                )
            ),
            "reaction_description": data["reactions"][0].get(
                "description", "No description"
            ),
            "cofactors_organic": "N/A",
            "cofactors_inorganic": "N/A",
            "organism": origin["organism"],
            "domain": origin["domain"],
            "kingdom": origin["kingdom"],
            "phylum": origin["phylum"],
            "class": origin["class"],
            "order": origin["order"],
            "family": origin["family"],
        }

        if val := data["enzyme"].get("cofactors", {}).get("organic", []):
            meta["cofactors_organic"] = "|".join(sorted(set(val)))

        if val := data["enzyme"].get("cofactors", {}).get("inorganic", []):
            meta["cofactors_inorganic"] = "|".join(sorted(set(val)))

        self.meta_gen["entries"][data["accession"]] = meta

    @staticmethod
    def get_taxonomy(data: dict) -> dict:
        """Download the organism identifier

        Arguments:
            data: mite entry

        Returns:
            A dict of organism info
        """
        origin = {
            "organism": "Not found",
            "domain": "Not found",
            "kingdom": "Not found",
            "phylum": "Not found",
            "class": "Not found",
            "order": "Not found",
            "family": "Not found",
        }

        if acc := data["enzyme"]["databaseIds"].get("uniprot"):
            if (
                response := requests.get(
                    f"https://rest.uniprot.org/uniprotkb/{acc}.json"
                )
            ).status_code == 200 or (
                response := requests.get(f"https://rest.uniprot.org/uniparc/{acc}.json")
            ).status_code == 200:
                content = response.json()
                record = content.get("organism", {}).get("lineage", None)
                try:
                    origin["domain"] = record[0] or "Not found"
                    origin["kingdom"] = record[1] or "Not found"
                    origin["phylum"] = record[2] or "Not found"
                    origin["class"] = record[3] or "Not found"
                    origin["order"] = record[4] or "Not found"
                    origin["family"] = record[5] or "Not found"
                    origin["organism"] = (
                        content.get("organism", {}).get("scientificName") or "Not found"
                    )
                except Exception as e:
                    logger.warning(
                        f"Did not find organism information for '{acc}' ({data["accession"]}): {e!s}"
                    )
                return origin

        if acc := data["enzyme"]["databaseIds"].get("genpept"):
            try:
                handle = Entrez.efetch(
                    db="protein", id=acc, rettype="gb", retmode="text"
                )
                record = SeqIO.read(handle, "genbank")
                origin["domain"] = record.annotations.get("taxonomy")[0] or "Not found"
                origin["kingdom"] = record.annotations.get("taxonomy")[1] or "Not found"
                origin["phylum"] = record.annotations.get("taxonomy")[2] or "Not found"
                origin["class"] = record.annotations.get("taxonomy")[3] or "Not found"
                origin["order"] = record.annotations.get("taxonomy")[4] or "Not found"
                origin["family"] = record.annotations.get("taxonomy")[5] or "Not found"
                origin["organism"] = record.annotations.get("organism") or "Not found"
                handle.close()
            except Exception as e:
                logger.warning(
                    f"Did not find organism information for '{acc}' ({data["accession"]}): {e!s}"
                )
            return origin

        return origin

    def extr_meta_mibig(self: Self, data: dict) -> None:
        """Extract and stores metadata with MIBiG IDs as keys

        retain only if:
        - mite entry has mibig accession
        - mite entry has a genbank accesssion
        - if mite genbank acc == mibig genbank acc

        add:
        - if no description, add placeholder description

        Params:
            data: the MITE JSON derived dict to extract data from

        """
        mite_acc = data["accession"]
        mibig_acc = data["enzyme"]["databaseIds"].get("mibig")
        if not mibig_acc:
            logger.warning(f"{mite_acc}: no MIBiG-accession - SKIP")
            return

        if mibig_acc not in self.mibig_data:
            logger.warning(
                f"{mite_acc}: {mibig_acc!s} is not found in MIBiG fasta file - SKIP"
            )
            return

        genpept = data["enzyme"]["databaseIds"].get("genpept")
        if not genpept:
            logger.warning(f"{mite_acc}: no GenPept-accession - SKIP")
            return

        if genpept not in self.mibig_data[mibig_acc]:
            logger.warning(
                f"{mite_acc}: GenPept-accession {genpept!s} is not found in the corresponding MIBiG BGC - SKIP"
            )
            return

        entry = {
            "mite_accession": mite_acc,
            "mite_url": f"https://bioregistry.io/mite:{mite_acc}",
            "status": data["status"],
            "enzyme_name": data["enzyme"]["name"],
            "enzyme_description": data["enzyme"].get(
                "description", "No description available"
            ),
            "enzyme_ids": data["enzyme"]["databaseIds"],
            "enzyme_tailoring": "|".join(
                sorted(
                    {
                        tailoring
                        for reaction in data.get("reactions")
                        for tailoring in reaction.get("tailoring", [])
                    }
                )
            ),
            "enzyme_refs": data["enzyme"]["references"],
        }

        if mibig_acc in self.meta_mibig["entries"]:
            self.meta_mibig["entries"][mibig_acc].append(entry)
        else:
            self.meta_mibig["entries"][mibig_acc] = [entry]
