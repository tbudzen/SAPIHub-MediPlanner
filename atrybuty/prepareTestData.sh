#!/bin/bash
echo "start"

SOURCE_FOLDER="/home/lkmiecik/sapihup/mediplanner/newgit/mediplanner/ewaluacja/atrybuty/original"
DEST_FOLDER="/home/lkmiecik/sapihup/mediplanner/newgit/mediplanner/atrybuty/test"

rm $DEST_FOLDER/*

for FILE in $SOURCE_FOLDER/*.ann; 
do
	echo "Preparing $DEST_FOLDER/$(basename -- "$FILE")"
	cat $FILE | grep -v -P '^A[0-9]+\t' > $DEST_FOLDER/$(basename -- "$FILE");
done

cp $SOURCE_FOLDER/*.txt $DEST_FOLDER/

# rm $DEST_FOLDER/mrakowski_patient_1415457.*

