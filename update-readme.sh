#! /bin/bash

find . -name "*.py" -perm -111 -type f -maxdepth 1 | while read line
do
echo '```'
python $line -h
echo '```'
done
