#!/bin/bash
DO_SETFILE=true

while getopts ":d" opt; do
  case ${opt} in
    d )
      DO_SETFILE=false
      ;;
    \? )
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    : )
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

DIR=.

find "$DIR" -type f -newermt "2023-03-05 00:00:00" ! -newermt "2023-03-06 00:00:00" -name "*.mp4" -print0 | while IFS= read -r -d '' FILE; do
  if [[ $FILE =~ (20[0-9]{2})([0-9]{2})([0-9]{2}) ]]; then
    YEAR=${BASH_REMATCH[1]}
    MONTH=${BASH_REMATCH[2]}
    DAY=${BASH_REMATCH[3]}
    DATE="${MONTH}/${DAY}/${YEAR} 00:00:00"
    DATE_FORMATTED=$(date -jf "%m/%d/%Y %H:%M:%S" "$DATE" +"%m/%d/%Y %I:%M:%S %p")
  else
    echo "Error: Filename does not contain expected format: " $FILE
    continue
  fi

  if $DO_SETFILE; then
    setfile -d "$DATE_FORMATTED" -m "$DATE_FORMATTED" "$FILE"
  else
    echo "$FILE"
  fi

done

