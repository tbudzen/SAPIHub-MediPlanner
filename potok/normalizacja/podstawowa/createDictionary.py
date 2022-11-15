# Przygotowuje slownik normalizacyjny w pliku <dict.tsv>, rejestrujac pojecie najczesciej przypisywane do nazwy, wg. normalizacji treningowych w katalogu <inputDir>
# Uzycie: python createDictionary.py <inputDir> <dict.tsv>

import sys
import os
import spacy

lemmatise=True
if lemmatise:
	nlp = spacy.load('pl_spacy_model')

inputDir=sys.argv[1]
outputFile=sys.argv[2]

normDict={}
namesDict={}
annoCache={}

def canonise(text):
	text=text.lower().replace(".","").replace(",","")
	if lemmatise:
		if not text in annoCache:
			annoCache[text]=" ".join([token.lemma_ for token in nlp(text)])
		text=annoCache[text]
	return(text)


counter=0
totalEnts=0
totalNorms=0
for filename in os.listdir(inputDir):
	counter=counter+1
	if not filename.endswith(".ann"):
		continue
	print("Processing "+str(counter)+"/"+str(len(os.listdir(inputDir)))+" "+filename+" ...")
	entities={}
	for line in open(os.path.join(inputDir, filename)):
		if not (line.startswith("T") and line[1].isdigit() and len(line.split("\t"))==3):
			continue
		totalEnts=totalEnts+1
		parts=line.split("\t")
		entities[parts[0]]=parts[2].strip()
	normalisations={}
	for line in open(os.path.join(inputDir, filename)):
		if not (line.startswith("N") and line[1].isdigit()):
			continue
		totalNorms=totalNorms+1
		parts=line.split("\t")[1].split(" ")
		icd=parts[2].upper()
		if len(line.split("\t"))==3:
			name=line.split("\t")[2].strip()
			namesDict[icd]=name
		normalisations[parts[1]]=icd
	for entity in entities:
		text=canonise(entities[entity])
		if not(text in normDict):
			normDict[text]={}
		concept="<NONE>"
		if entity in normalisations:
			concept=normalisations[entity]
		if concept in normDict[text]:
			normDict[text][concept]=normDict[text][concept]+1
		else:
			normDict[text][concept]=1
	print("Have "+str(len(entities))+" entities with "+str(len(normalisations))+" normalisations.")

output=open(outputFile,"w")
for text in normDict:
	bestICD=""
	bestFreq=0
	allFreq=0
	for icd10 in normDict[text]:
		allFreq=allFreq+normDict[text][icd10]
		if icd10=='<NONE>':
			continue
		if normDict[text][icd10]>bestFreq:
			bestFreq=normDict[text][icd10]
			bestICD=icd10
	bestName=""
	if bestICD in namesDict:
		bestName=namesDict[bestICD]
	if bestICD!='<NONE>' and bestICD!='':
		output.write(text+"\t"+bestICD+"\t"+str(bestFreq)+"\t"+str(allFreq)+"\t"+bestName+"\n")
output.close()

print("Total entities: "+str(totalEnts)+" normalisations:"+str(totalNorms))

