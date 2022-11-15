import os
import re
import sys

prefix='./'

# PREPARE
exec(open(prefix+'conversion.py').read())
def tokenToLine(tokenInfo,keepTags,headerTag):
    token = tokenInfo.token
    cells = []
    cells.append(token.text.strip())
    cells.append(token.lemma_.strip())
    cells.append(token.tag_)
    cells.append(tokenInfo.getFirstMeshPolTagStr())
    cells.append(tokenInfo.getMedicineTagCell())
    cells.append(headerTag)
    if keepTags:
        cells.append(tokenInfo.tag)
    else:
        cells.append(str(tokenInfo.startIndex))
        cells.append(str(len(token.text)))
    emptyLine = ""
    if tokenInfo.isLastInSentence:
        emptyLine = "\n"
    return "\t".join(cells) + "\n" + emptyLine

# PARAMS
isMeshPolsFromCache = True
isMedicinesFromCache = True
keepTags=None
if sys.argv[3]=='1':
	keepTags=True
else:
	keepTags=False

# INPUT FILES
distinctMeshPolTags = prefix+"distinctMeshPolTags.txt"
meshpolFile = prefix+"meshpol.tsv"
meshpolFileCache = prefix+"meshpol_cache.json"
medicinesFile = prefix+"rpo.tsv"
medicinesFileCache = prefix+"medicines_cache.json"
inputDir=sys.argv[1]

# OUTPUT FILE
outputDir =  sys.argv[2]

# PREPARE
selectedMeshPolTags = list(map(lambda line: MeshPolTag(line), linesFromFile(distinctMeshPolTags)))
print(len(selectedMeshPolTags))
meshPols = getMeshPols(isMeshPolsFromCache, meshpolFile, selectedMeshPolTags, meshpolFileCache)
medicines = getMedicines(isMedicinesFromCache, medicinesFile, medicinesFileCache)

# DO
for filename in os.listdir(inputDir):
	if not filename.endswith(".ann"):
		continue
	outPath=os.path.join(outputDir, re.sub('\\.ann$','.crf',filename))
	if os.path.exists(outPath):
		print("Skipping "+filename+" ...")
		continue
	print("Processing "+filename+" ...")
	annotations = os.path.join(inputDir, filename)
	full_text = os.path.join(inputDir, re.sub('\\.ann$','.txt',filename))
	tags = tagsFromFile(annotations)
	text = textFromFile(full_text)
	tokens = tokensFromAnnotations1(text, tags)
	tokens = updateWithMeshTags(tokens, meshPols, list(map(lambda meshTag: meshTag.name,selectedMeshPolTags)))
	tokens = updateWithMedicines(tokens, medicines)
	tmpPath=os.path.join(outputDir, re.sub('\\.ann$','.tmp',filename))
	outF=open(tmpPath,"w")
	prevHeader=""
	currHeader=None
	currSpaces=0
	for token in tokens:
		# check the current header
		headerTag="o"
		if token.token.text.startswith("-----"):
			if currHeader is None:
				currHeader=""
			prevHeader=currHeader
			currHeader=None
			currSpaces=0
		elif token.token.tag_=="_SP":
			currSpaces=currSpaces+1
			if currSpaces==3:
				currHeader=""
		elif currHeader is None:
			currHeader=token.token.text.strip().lower()
		# add previous header to features
		if prevHeader!="" and not token.token.text.startswith("-----") and not currHeader is None:
			headerTag="i-"+prevHeader
		# write it out
		line = tokenToLine(token,keepTags,headerTag)
		outF.write(line)
	outF.write("\n")
	outF.close()
	os.rename(tmpPath,outPath)
        


