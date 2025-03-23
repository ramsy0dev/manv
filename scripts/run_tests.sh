#!/usr/bin/bash

set -xr

for file in tests/variables/*; do    
    poetry run manv --file-path "$file"
done
