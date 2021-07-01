#!/usr/bin/bash

for FILE in villarrica/*
do
	echo $FILE
	date=$(echo $FILE | awk -F '[_.]' '{print $3 20 $2 0 0}')
	#echo $date
	littler -n $FILE -i '' -d $date -s balloon -o $FILE'.littler' -t graw $FILE
done
