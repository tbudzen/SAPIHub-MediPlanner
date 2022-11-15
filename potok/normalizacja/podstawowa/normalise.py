# Wczytuje anotacje z katalogu <inputDir>, normalizuje je wedlug slownika <dict.tsv> i umieszcza wyniki w katalogu <outputDir> 
# Uzycie: python normalise.py <inputDir> <outputDir> <dict.tsv>

from shutil import copyfile
import os,sys,re
import spacy

lemmatise=True
if lemmatise:
	nlp = spacy.load('pl_spacy_model')

inputDir=sys.argv[1]
outputDir =sys.argv[2]
dictPath=sys.argv[3]

normDict={}
namesDict={}
for line in open(dictPath):
	parts=line.split("\t")
	text=parts[0]
	icd=parts[1]
	name=parts[4].strip()
	normDict[text]=icd
	if name!="":
		namesDict[icd]=name
		#normDict[name.lower()]=icd
annoCache={}

print("Read "+str(len(namesDict))+" different codes.")
def canonise(text):
	text=text.lower().replace(".","").replace(",","")
	if lemmatise:
		if not text in annoCache:
			annoCache[text]=" ".join([token.lemma_ for token in nlp(text)])
		text=annoCache[text]
	return(text)

		
for filename in os.listdir(inputDir):
	if not filename.endswith(".ann"):
		continue
	print("Processing "+filename+" ...")
	annFile = os.path.join(inputDir, filename)
	textFile = os.path.join(inputDir, re.sub('\\.ann$','.txt',filename))
	outPath=os.path.join(outputDir, filename)
	copyfile(annFile,outPath)
	outFile=open(outPath,"a")
	counter=1
	for line in open(annFile):
		if not (line.startswith("T") and line[1].isdigit() and len(line.split("\t"))==3):
			continue
		tid=line.split("\t")[0]
		text=canonise(line.split("\t")[2].strip())
		parts=text.split(" ")
		for i in range(len(parts)):
			partsin=parts[0:(len(parts)-i)]
			shorttext=" ".join(partsin)
			#if len(shorttext)<=0.5*len(text):
			#	break
			if shorttext in normDict:
				name=""
				icd=normDict[shorttext]
				if icd in namesDict:
					name=namesDict[icd]
				outFile.write("N"+str(counter)+"\tReference "+tid+" "+icd+"\t"+name+"\n")
				counter=counter+1
				break
			#break
	outFile.close()
        


