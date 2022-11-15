from shutil import copyfile
import os,sys,re

from nlp_pipeline.relations.relations import RelationsUtils


class MyRelations():

	nlp = None

	def __init__(self, nlp0):
		self.nlp = nlp0

	def process_relations(self, input_dir, output_dir):

		print("process_relations CWD: " + os.getcwd())

		#prefix = '../'
		#exec(open(prefix + 'relations.py').read())

		inputDir = input_dir
		outputDir = output_dir

		for filename in os.listdir(inputDir):
			if not filename.endswith(".ann"):
				continue
			outPath=os.path.join(outputDir, filename)
			# todo: commented below to overwrite
			if os.path.exists(outPath):
				print("Skipping "+filename+" ...")
				continue
			print("Processing "+filename+" ...")
			annFile = os.path.join(inputDir, filename)
			textFile = os.path.join(inputDir, re.sub('\\.ann$','.txt',filename))
			tmpPath=os.path.join(outputDir, re.sub('\\.ann$','.tmp',filename))
			# process here
			ru = RelationsUtils(self.nlp)
			tags = ru.tagsFromFile(annFile)
			text = ru.textFromFile(textFile)
			copyfile(annFile,tmpPath)

			try:
				(relations, sentences) = ru.findSuspectRelations(tags, text)
				#print(str(relations))
				ru.removeRedundantRelations(relations, sentences,2)
				relations = list(filter(lambda relation: not relation.removed, relations))
				print("Adding " + str(len(relations)) + " relations...")
				ru.appendRelationsToFile(relations, tmpPath)
			except AttributeError as e:
				print("AttributeError: " + str(e))

			# process finished
			os.rename(tmpPath,outPath)
