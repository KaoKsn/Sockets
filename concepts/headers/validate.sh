#!/usr/bin/env bash

set -euo pipefail

echo "Cleaning if required.."
rm -f *.txt *.dat >/dev/null

printf "Extracting data files..\n"
unzip tcp_data.zip >/dev/null

for i in {0..9}; do
	echo "+[$((i + 1))]: Validating TCP header"
	python validator.py tcp_addrs_"$i".txt tcp_data_"$i".dat | sed 's/^/\t/'
	echo
done

echo "Cleaning.."
rm -f *.txt *.dat >/dev/null
