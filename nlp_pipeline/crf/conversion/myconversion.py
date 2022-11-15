import os
import re
import sys

from nlp_pipeline.crf.conversion.conversion import ConversionUtils

from nlp_pipeline.crf.conversion.conversion import MeshPolTag


class MyConversion():

	nlp = None

	def __init__(self, nlp0):
		self.nlp = nlp0
		print("MyConversion, nlp = " + str(self.nlp))

	def my_conversion(self, input_dir, output_dir, keep_tags):

		#prefix='./'
		prefix = "crf/conversion/"

		# PREPARE
		#print("cwd: " + os.getcwd())
		#exec(open(prefix+'conversion.py').read())

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
		if keep_tags=='1':
			keepTags=True
		else:
			keepTags=False

		# INPUT FILES

		distinctMeshPolTags = prefix+"distinctMeshPolTags.txt"
		meshpolFile = prefix+"meshpol.tsv"
		meshpolFileCache = prefix+"meshpol_cache.json"
		medicinesFile = prefix+"rpo.tsv"
		medicinesFileCache = prefix+"medicines_cache.json"

		inputDir=input_dir

		# OUTPUT FILE
		outputDir = output_dir

		myconv = ConversionUtils(self.nlp)

		# PREPARE
		selectedMeshPolTags = []
		meshPols = []
		medicines = []
		prepared = False
		if not prepared:
			selectedMeshPolTags = list(map(lambda line: MeshPolTag(line),
										   myconv.linesFromFile(distinctMeshPolTags)))
			print(len(selectedMeshPolTags))

			meshPols = myconv.getMeshPols(isMeshPolsFromCache, meshpolFile, selectedMeshPolTags, meshpolFileCache)
			medicines = myconv.getMedicines(isMedicinesFromCache, medicinesFile, medicinesFileCache)

			prepared = True

		# DO
		for filename in os.listdir(inputDir):
			#if not filename.endswith(".ann"):
			#	print("Skipping not ann "+filename+" ...")
			#	continue
			#elif not keepTags and not filename.endswith(".txt"):
			#	print("Skipping not txt "+filename+" ...")
			#	continue
			outPath=os.path.join(outputDir, re.sub('\\.txt$','.crf',filename)) # todo: was .ann
			print("outPath = " + outPath)
			if os.path.exists(outPath):
				print("Deleting "+outPath+" ...")
				os.remove(outPath)
				continue
			print("Processing "+filename+" ...")
			annotations = os.path.join(inputDir, filename)
			full_text = os.path.join(inputDir, re.sub('\\.ann$','.txt',filename))
			if keepTags:
				tags = myconv.tagsFromFile(annotations)
			else:
				tags = []
			text = myconv.textFromFile(full_text)
			tokens = myconv.tokensFromAnnotations1(text, tags, selectedMeshPolTags)
			tokens = myconv.updateWithMeshTags(tokens, meshPols, list(map(lambda meshTag: meshTag.name,selectedMeshPolTags)))
			tokens = myconv.updateWithMedicines(tokens, medicines)
			tmpPath=os.path.join(outputDir, re.sub('\\.ann$','.tmp',filename))
			print("cwd = " + os.getcwd())
			outF=open(tmpPath,"w", encoding="utf-8", errors='ignore')
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
				try:
					outF.write(line)
				except UnicodeEncodeError as e:
					print("myconversion: UnicodeEncodeError")
			outF.write("\n")
			outF.close()
			print("Renaming cwd = " + os.getcwd())
			print("Renaming " + tmpPath + " to " + outPath)
			os.rename(tmpPath,outPath)
