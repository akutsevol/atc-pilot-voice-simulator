#!/bin/bash

set -euo pipefail

rate=180
div=1
while true
do
  for i in {1..10}
  do
     txt=$(( $RANDOM / ${div} ))
     echo -n "${txt} "
     say -r ${rate} ${txt}
     sleep 1
  done
  echo -n "..."
  read -n 1
done
