#!/bin/bash

dir=src/

SECONDS=0

LINT=$( isort --profile black ${dir} && black ${dir})
echo "Lint time: $SECONDS"

COMPILE=$((python3 ${dir}core.py --instr $1 generate -t il > core.il) 2>&1)
echo "Py time: $SECONDS"
if [[ "$COMPILE" !=  "" ]]; then
	echo "$COMPILE"
else
	FORMAL="sby -f ${dir}core.sby"
	RESULT=$($FORMAL | grep 'DONE\|Assert failed')
	echo "$RESULT"
	echo "Total time: $SECONDS"
fi
