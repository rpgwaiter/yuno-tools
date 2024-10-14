#!/usr/bin/env bash
# This assumes nix and built tools

## TODO:
# - package with nix
# - flags for different outputs

# Working dir
WORKDIR="${PWD}/decomp"

# Path to untouched yu-no .ARC files
YUNO_DIR="${PWD}/data"

# Ensure dirs exist
mkdir -p "${WORKDIR}" "${YUNO_DIR}"

# Ensure you have some .ARC files
ARC_FILES=$(\ls -1 "${YUNO_DIR}/"*.ARC) # full paths
ARC_COUNT=$( echo "${ARC_FILES}" | wc -l)
if [[ $ARC_COUNT -lt 1 ]]
then
  exit 1 # TODO: Cleanup/error message
fi

# Ensure you have yu-no tools
## TODO:

echo $ARC_FILES
for i in $ARC_FILES
do
  echo "LOOPING, i=${i}"
  THIS=$(basename "${i%.*}") # removes the file ext
  THIS_OUT="${WORKDIR}/${THIS}"
  mkdir -p "${THIS_OUT}"
  # Extract with yuno tools
  nix shell .#yuno-scripts -c arcunpack -- "${i}" "${THIS_OUT}"
done


## Convert all .WAV files to opus
## TODO: (dont) replace wav flag
