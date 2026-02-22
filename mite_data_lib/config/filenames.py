class Filenames:
    """Centralized filename config"""

    @property
    def meta_artifact(self) -> str:
        return "artifact_metadata.json"

    @property
    def smarts(self) -> str:
        return "dump_smarts.csv"

    @property
    def smiles(self) -> str:
        return "dump_smiles.csv"

    @property
    def summary_json(self) -> str:
        return "metadata_general.json"

    @property
    def summary_mibig(self) -> str:
        return "metadata_mibig.json"

    @property
    def summary_csv(self) -> str:
        return "summary.csv"

    @property
    def prot_acc(self) -> str:
        return "mite_prot_accessions.csv"

    @property
    def product(self) -> str:
        return "product_list.pickle"

    @property
    def reaction(self) -> str:
        return "reaction_fps.pickle"

    @property
    def substrate(self) -> str:
        return "substrate_list.pickle"

    @property
    def mibig_prot(self) -> str:
        return "mibig_proteins.json"

    @property
    def mibig_meta(self) -> str:
        return "metadata.json"


names = Filenames()
