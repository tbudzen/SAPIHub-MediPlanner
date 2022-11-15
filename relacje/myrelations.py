from shutil import copyfile
import os,sys,re

prefix='./'

exec(open(prefix+'relations.py').read())

inputDir=sys.argv[1]
outputDir =  sys.argv[2]

for filename in os.listdir(inputDir):
	if not filename.endswith(".ann"):
		continue
	outPath=os.path.join(outputDir, filename)
	if os.path.exists(outPath):
		print("Skipping "+filename+" ...")
		continue
	print("Processing "+filename+" ...")
	annFile = os.path.join(inputDir, filename)
	textFile = os.path.join(inputDir, re.sub('\\.ann$','.txt',filename))
	tmpPath=os.path.join(outputDir, re.sub('\\.ann$','.tmp',filename))
	# process here
	tags = tagsFromFile(annFile)
	text = textFromFile(textFile)
	copyfile(annFile,tmpPath)
	(relations, sentences) = findSuspectRelations(tags, text)
	removeRedundantRelations(relations, sentences,2)
	relations = list(filter(lambda relation: not relation.removed, relations))
	appendRelationsToFile(relations, tmpPath)
	# process finished
	os.rename(tmpPath,outPath)
        


