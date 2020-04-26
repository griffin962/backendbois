#!/bin/bash

FILE=./test.db
if test -f "$FILE"; then
	rm "$FILE"
fi

cd ./Examples
python seed_db.py

