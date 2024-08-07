"""Helper script to automatically generate pngs of alphafold pdbs"""

import json
from pathlib import Path

from alphafetcher import AlphaFetcher
import pymol2

dir_data = Path(__file__).parent.joinpath("data")
dir_pdb = Path(__file__).parent.joinpath("pdb")
dir_img = Path(__file__).parent.joinpath("img")


def extract_uniprot_ids() -> list:
    """Extracts uniprot Ids from mite entries

    Returns:
        A list with uniprot ids
    """
    uniprot_ids = set()

    for infile in dir_data.iterdir():
        with open(infile) as file_in:
            json_dict = json.load(file_in)

        if enzyme := json_dict.get("enzyme", {}).get("databaseIds").get("uniprot"):
            uniprot_ids.add(enzyme)

    return list(uniprot_ids)


def download_pdbs() -> None:
    """Use AlphaFetcher to download pdbs"""
    uni_ids = extract_uniprot_ids()

    if len(uni_ids) == 0:
        raise RuntimeError("No uniprot IDs collected - ABORT.")

    nonred_ids = []
    for uni in uni_ids:
        if not dir_pdb.joinpath(f'{uni}.pdb').exists():
            nonred_ids.append(uni)

    if len(nonred_ids) == 0:
        return

    fetcher = AlphaFetcher(base_savedir=str(dir_pdb))
    fetcher.add_proteins(proteins=nonred_ids)
    fetcher.download_all_files(pdb=True, multithread=True, workers=4)

    for infile in dir_pdb.joinpath("pdb_files").iterdir():
        infile.rename(dir_pdb / infile.name)

    dir_pdb.joinpath("pdb_files").rmdir()


def store_pngs() -> None:
    """Use pymol to generate png images from pdb files in pdb dictionary"""
    for infile in dir_pdb.iterdir():
        outfile = dir_img.joinpath(f'{infile.stem}.png')
        if not outfile.exists():
            with pymol2.PyMOL() as pymol:
                pymol.cmd.load(str(infile))
                pymol.cmd.bg_color("white")
                pymol.cmd.hide("everything")
                pymol.cmd.show("cartoon")
                pymol.cmd.spectrum("count", "rainbow", selection="all")
                pymol.cmd.png(str(outfile), dpi=600)


def main():
    download_pdbs()
    store_pngs()


if __name__ == "__main__":
    main()
