#!/bin/bash

dir=src/

SECONDS=0

LINT=$( isort --profile black ${dir}alu.py && black ${dir}alu.py)
echo "Lint time: $SECONDS"

COMPILE=$((python3 ${dir}alu.py --oper $1 generate -t il > alu.il) 2>&1)
echo "Py time: $SECONDS"
if [[ "$COMPILE" !=  "" ]]; then
	echo "$COMPILE"
else
	FORMAL="sby -f ${dir}alu.sby"
	RESULT=$($FORMAL | grep 'DONE\|Assert failed')
	echo "$RESULT"
	echo "Total time: $SECONDS"
fi
