import concurrent.futures
import logging
from pathlib import Path

import requests
from Bio import Entrez

from mite_data_lib.config.config import settings

logger = logging.getLogger(__name__)
Entrez.email = settings.email


class SequenceService:
    """Manages downloading of sequences"""

    def __init__(self, fasta: Path | None = None, timeout: float | None = None):
        self.fasta = fasta or settings.data / "fasta"
        self.timeout = timeout or settings.timeout

    def fetch_ncbi(self, acc: str) -> list[str]:
        """Download protein seq from NCBI

        Args:
            acc: An NCBI accession

        Raises:
            RuntimeError: error during download

        Returns:
            protein sequence as fasta-formatted list of strings
        """

        def _fetch(ncbi: str):
            handle = Entrez.efetch(
                db="protein", id=ncbi, rettype="fasta", retmode="text"
            )
            data = handle.read().strip()
            handle.close()
            return data

        with concurrent.futures.ThreadPoolExecutor() as ex:
            future = ex.submit(_fetch, acc)

            try:
                fasta_data = future.result(timeout=self.timeout)
            except concurrent.futures.TimeoutError as e:
                raise RuntimeError("Warning: could not connect to NCBI: Timeout") from e

        lines = fasta_data.splitlines()
        if not lines or len(lines) == 1:
            raise RuntimeError(f"No sequence found for GenBank Accession {acc}")

        return lines[1:]

    def fetch_uniprot(self, acc: str) -> list[str]:
        """Download protein seq from uniprot

        Args:
            acc: A uniprot accession

        Raises:
            RuntimeError: error during download

        Returns:
            protein sequence as fasta-formatted list of strings
        """

        def _service(uniprot: str) -> str:
            if uniprot.startswith("UPI"):
                return f"https://rest.uniprot.org/uniparc/{uniprot}.fasta"
            else:
                return f"https://rest.uniprot.org/uniprotkb/{uniprot}.fasta"

        try:
            response = requests.get(_service(acc), timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.ConnectTimeout as e:
            raise RuntimeError("Could not connect to UniProt: Timeout") from e
        except requests.HTTPError as e:
            raise RuntimeError(f"Fetching Uniprot ID {acc} lead to HttpError") from e

        lines = response.text.strip().splitlines()
        if len(lines) <= 1:
            raise RuntimeError(f"UniProt download provided no sequence for ID {acc}")
        return lines[1:]

    def seq_match(self, genpept: str, uniprot: str) -> bool:
        """Check if protein sequences are equal"""
        return "".join(self.fetch_ncbi(genpept)) == "".join(self.fetch_uniprot(uniprot))

    def dump_fasta(self, mite_acc: str, acc: str, seq: list[str]) -> None:
        path = self.fasta / f"{mite_acc}.fasta"
        with open(path, "w") as f:
            f.write(f">{mite_acc} {acc}\n{'\n'.join(seq)}")
