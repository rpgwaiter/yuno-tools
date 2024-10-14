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

# Ensure you have yu-no tools, ffmpeg, etc
## TODO:

for i in $ARC_FILES
do
  echo "LOOPING, i=${i}"
  THIS=$(basename "${i%.*}") # removes the file ext
  THIS_OUT="${WORKDIR}/${THIS}"
  mkdir -p "${THIS_OUT}"
  # Extract with yuno tools
  nix shell .#yuno-scripts -c arcunpack -- "${i}" "${THIS_OUT}"
done

## Convert all GP8 -> bmp
## TODO: Maybe bmp -> something with lossless compression?


## Convert all .WAV files to opus
## TODO: (dont) replace wav flag
## - this should happen after the voice patch
WAV_FILES=$(ls -1 "${WORKDIR}/"**"/"*".WAV")
WAV_TOTAL_SIZE=$(du -ch $WAV_FILES | tail -1 | awk '{print $1}')

for i in $WAV_FILES
do
  THIS="${i%.*}" # removes the file ext
  THIS_OUT="${THIS}.FLAC"
  if [ ! -f "${THIS_OUT}" ]; then
    echo "Converting: $(basename ${THIS})"
    ffmpeg -hide_banner -loglevel error -i "${i}" -af aformat=s16:44100 "${THIS_OUT}"
  fi
done

FLAC_FILES=$(ls -1 "${WORKDIR}/"**"/"*".FLAC")
FLAC_TOTAL_SIZE=$(du -ch $FLAC_FILES | tail -1 | awk '{print $1}')

echo "Done converting .WAV to .FLAC"
echo "Total size of .wav files: $WAV_TOTAL_SIZE"
echo "Total size of .flac files: $FLAC_TOTAL_SIZE"
