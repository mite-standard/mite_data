"""Creates auxiliary files for mite_web

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
import pickle
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, DirectoryPath
from rdkit.Chem import PandasTools, rdChemReactions

logger = logging.getLogger(__name__)


class MolFileManager(BaseModel):
    """Prepare auxiliary molecule files for mite web

    Only entries with "active" flag are used to compile auxiliary files

    Attributes:
        src: mite entries location
        trgt: metadata location
        smiles: dict of SMILES be exported as csv file
        smarts: dict of reaction SMARTS to be exported as csv file
        pickle_substrates: list with pre-calculated fingerprints for substructure search
        pickle_products: list with pre-calculated fingerprints for substructure search
        pickle_smartsfps: dict with pre-calculated reaction smarts fingerprints for search
    """

    src: DirectoryPath = Path(__file__).parent.parent.joinpath("data/")
    trgt: DirectoryPath = Path(__file__).parent.parent.joinpath("metadata/")
    smiles: dict = {"mite_id": [], "substrates": [], "products": []}
    smarts: dict = {
        "mite_id": [],
        "reactionsmarts": [],
    }
    pickle_substrates: list = []
    pickle_products: list = []
    pickle_smartsfps: dict = {
        "mite_id": [],
        "reactionsmarts": [],
        "reaction_fps": [],
        "diff_reaction_pfs": [],
    }

    def prepare_files(self) -> None:
        """Prepare the auxiliary files derived from mite entries

        Only "active" entries are dumped; others are skipped
        """
        for entry in self.src.iterdir():
            with open(entry) as infile:
                mite_data = json.load(infile)

            if mite_data["status"] != "active":
                continue

            self.prepare_smiles(mite_data)
            self.prepare_smarts(mite_data)

        self.prepare_pickled_smiles()
        self.prepare_pickled_smarts()

    def prepare_smiles(self, data: dict) -> None:
        """Create a table of SMILES strings contained in MITE entries

        Arguments:
            data: a dict derived from a mite json file
        """
        for readctionid, reaction in enumerate(data["reactions"], 1):
            for exampleid, example in enumerate(reaction["reactions"], 1):
                self.smiles["mite_id"].append(
                    f"{data['accession']}.reaction{readctionid}.example{exampleid}"
                )
                self.smiles["substrates"].append(f"{example['substrate']}")
                self.smiles["products"].append(f"{'.'.join(example['products'])}")

    def prepare_smarts(self, data: dict) -> None:
        """Create a table of reaction SMARTS strings contained in MITE entries

        Arguments:
            data: a dict derived from a mite json file
        """
        for readctionid, reaction in enumerate(data["reactions"], 1):
            self.smarts["mite_id"].append(f'{data['accession']}.reaction{readctionid}')
            self.smarts["reactionsmarts"].append(f"{reaction["reactionSMARTS"]}")

    def prepare_pickled_smiles(self) -> None:
        """Create a pickle file with pre-calculated SMILES fingerprints"""
        df = pd.DataFrame(self.smiles)

        PandasTools.AddMoleculeColumnToFrame(
            df,
            smilesCol="substrates",
            molCol="ROMol_substrates",
            includeFingerprints=True,
        )
        PandasTools.AddMoleculeColumnToFrame(
            df, smilesCol="products", molCol="ROMol_products", includeFingerprints=True
        )

        self.pickle_substrates = list(df["ROMol_substrates"])
        self.pickle_products = list(df["ROMol_products"])

    def prepare_pickled_smarts(self) -> None:
        """Create a pickle file of a dict with pre-calculated reaction SMARTS fingerprints"""
        self.pickle_smartsfps["mite_id"] = self.smarts.get("mite_id")
        self.pickle_smartsfps["reactionsmarts"] = self.smarts.get("reactionsmarts")

        for smarts in self.smarts.get("reactionsmarts"):
            self.pickle_smartsfps["reaction_fps"].append(
                rdChemReactions.CreateStructuralFingerprintForReaction(
                    rdChemReactions.ReactionFromSmarts(smarts)
                )
            )
            self.pickle_smartsfps["diff_reaction_pfs"].append(
                rdChemReactions.CreateDifferenceFingerprintForReaction(
                    rdChemReactions.ReactionFromSmarts(smarts)
                )
            )

    def dump_files(self) -> None:
        """Dump the assembled files"""
        df_smiles = pd.DataFrame(self.smiles)
        df_smiles.to_csv(path_or_buf=self.trgt.joinpath("dump_smiles.csv"))

        df_smarts = pd.DataFrame(self.smarts)
        df_smarts.to_csv(path_or_buf=self.trgt.joinpath("dump_smarts.csv"))

        with open(self.trgt.joinpath("substrate_list.pickle"), "wb") as outfile:
            pickle.dump(obj=self.pickle_substrates, file=outfile)

        with open(self.trgt.joinpath("product_list.pickle"), "wb") as outfile:
            pickle.dump(obj=self.pickle_products, file=outfile)

        with open(self.trgt.joinpath("reaction_fps.pickle"), "wb") as outfile:
            pickle.dump(obj=self.pickle_smartsfps, file=outfile)
