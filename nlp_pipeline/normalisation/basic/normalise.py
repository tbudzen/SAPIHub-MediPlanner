# Wczytuje anotacje z katalogu <inputDir>, normalizuje je wedlug slownika <dict.tsv> i umieszcza wyniki w katalogu <outputDir> 
# Uzycie: python normalise.py <inputDir> <outputDir> <dict.tsv>

from shutil import copyfile
import os,sys,re
import spacy


class Normalisation():
	annoCache = {}
	#lemmatise = False

	nlp = None

	def __init__(self, nlp0):
		self.nlp = nlp0

	def normalise(self, input_dir, output_dir, dict_path):

		lemmatise=True
		#if lemmatise:
		#	nlp = spacy.load('pl_spacy_model')

		inputDir = input_dir
		outputDir = output_dir
		dictPath = dict_path

		normDict={}
		namesDict={}
		try:
			for line in open(dictPath, encoding="utf-8", errors='ignore'):
				parts=line.split("\t")
				text=parts[0]
				icd=parts[1]
				name=parts[4].strip()
				normDict[text]=icd
				if name!="":
					namesDict[icd]=name
					#normDict[name.lower()]=icd
		except UnicodeDecodeError as e:
			print("UnicodeDecodeError in normalise.py")

		print("Read "+str(len(namesDict))+" different codes.")


		def canonise(text):
			text=text.lower().replace(".","").replace(",","")
			if lemmatise:
				if not text in self.annoCache:
					self.annoCache[text]=" ".join([token.lemma_ for token in self.nlp(text)])
				text=self.annoCache[text]
			return(text)


		for filename in os.listdir(inputDir):
			if not filename.endswith(".ann"):
				continue
			print("Processing "+filename+" ...")
			annFile = os.path.join(inputDir, filename)
			textFile = os.path.join(inputDir, re.sub('\\.ann$','.txt',filename))
			outPath=os.path.join(outputDir, filename)
			copyfile(annFile,outPath)
			outFile=open(outPath,"a", encoding="utf-8", errors='ignore')
			#outFile.write("\n") # todo: check - ok if commented, attributes annotator lacked of "\n"
			counter=1
			try:
				for line in open(annFile, encoding="utf-8", errors='ignore'):
					#print("Normalise line: [" + line + "]")
					if not (line.startswith("T") and line[1].isdigit() and len(line.split("\t"))==3):
						continue
					tid=line.split("\t")[0]
					text=canonise(line.split("\t")[2].strip())
					#sprint("Canonised text is: " + text)
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
				print("Normalisations added: " + str(counter - 1))
			except UnicodeDecodeError as e:
				print("UnicodeDecodeError: " + str(e))
			outFile.close()



