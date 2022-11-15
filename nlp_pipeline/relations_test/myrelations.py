from shutil import copyfile
import os,sys,re

from relations import RelationsUtils
from evaluation import Evaluation
from attributes import Attributes

class MyRelations():

	def process_relations(self, nlp, input_dir, output_dir):

		print("process_relations CWD: " + os.getcwd())

		#prefix = '../'
		#exec(open(prefix + 'relations.py').read())

		inputDir = input_dir
		outputDir = output_dir

		ru = RelationsUtils(nlp)

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
			tags = ru.tagsFromFile(annFile)
			text = ru.textFromFile(textFile)
			copyfile(annFile,tmpPath)

			(relations, sentences) = ru.findSuspectRelations(tags, text)
			ru.removeRedundantRelations(relations, sentences,2)
			relations = list(filter(lambda relation: not relation.removed, relations))
			ru.appendRelationsToFile(relations, tmpPath)

			# process finished
			os.rename(tmpPath,outPath)


if __name__ == "__main__":
	attr = Attributes()
	attr.strip_annotations("test_input", "R")
	mr = MyRelations()
	mr.process_relations("test_input", "test_pred")
	ev = Evaluation()
	ev.evaluate("original", "test_pred", "result.tsv")

