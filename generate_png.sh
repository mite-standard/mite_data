#!/bin/bash

for pdb_file in pdb/*.pdb; do
    base_name=$(basename "$pdb_file" .pdb)
    pymol-oss.pymol "$pdb_file" -d "bg_color white; hide everything; show cartoon; spectrum count, red blue; set opaque_background, 0; png img/$base_name.png, 0, 0, -1, ray=1; quit;"
done