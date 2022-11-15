# Przygotowuje slownik normalizacyjny w pliku <dict.tsv>, rejestrujac pojecie najczesciej przypisywane do nazwy, wg. normalizacji treningowych w katalogu <inputDir>
# Uzycie: python createDictionary.py <inputDir> <dict.tsv>

import os

from nlp_pipeline.normalisation.basic.normalise import Normalisation


class DictionaryCreation():
    nlp = None

    def __init__(self, nlp0):
        self.nlp = nlp0
        print("DictionaryCreation, nlp = " + str(self.nlp))

    def canonise(self, text):
        norm = Normalisation(self.nlp)
        text = text.lower().replace(".", "").replace(",", "")
        lemmatise = True
        if lemmatise:
            if not text in norm.annoCache:
                norm.annoCache[text] = " ".join([token.lemma_ for token in self.nlp(text)])  # norm.nlp(text)])
            text = norm.annoCache[text]
        return (text)

    def dictionary_create(self, input_dir, output_dir):

        lemmatise = True
        # if lemmatise:
        #	print("Loading pl_spacy_model...")
        #	nlp = spacy.load('pl_spacy_model')
        #	print("pl_spacy_model loaded.")

        inputDir = input_dir
        outputFile = output_dir

        normDict = {}
        namesDict = {}
        annoCache = {}

        counter = 0
        totalEnts = 0
        totalNorms = 0
        for filename in os.listdir(inputDir):
            counter = counter + 1
            if not filename.endswith(".ann"):
                continue
            print("Processing " + str(counter) + "/" + str(len(os.listdir(inputDir))) + " " + filename + " ...")
            entities = {}
            try:
                for line in open(os.path.join(inputDir, filename), encoding="utf-8", errors='ignore'):
                    if not (line.startswith("T") and line[1].isdigit() and len(line.split("\t")) == 3):
                        continue
                    totalEnts = totalEnts + 1
                    parts = line.split("\t")
                    entities[parts[0]] = parts[2].strip()
                normalisations = {}
                for line in open(os.path.join(inputDir, filename), encoding="utf-8", errors='ignore'):
                    if not (line.startswith("N") and line[1].isdigit()):
                        continue
                    totalNorms = totalNorms + 1
                    parts = line.split("\t")[1].split(" ")
                    icd = parts[2].upper()
                    if len(line.split("\t")) == 3:
                        name = line.split("\t")[2].strip()
                        namesDict[icd] = name
                    normalisations[parts[1]] = icd
            except UnicodeDecodeError as e:
                print("UnicodeDecodeError: " + str(e))
            for entity in entities:
                text = self.canonise(entities[entity])
                if not (text in normDict):
                    normDict[text] = {}
                concept = "<NONE>"
                if entity in normalisations:
                    concept = normalisations[entity]
                if concept in normDict[text]:
                    normDict[text][concept] = normDict[text][concept] + 1
                else:
                    normDict[text][concept] = 1
            print("Have " + str(len(entities)) + " entities with " + str(len(normalisations)) + " normalisations.")

        output = open(outputFile, "w", encoding="utf-8", errors='ignore')
        for text in normDict:
            bestICD = ""
            bestFreq = 0
            allFreq = 0
            for icd10 in normDict[text]:
                allFreq = allFreq + normDict[text][icd10]
                if icd10 == '<NONE>':
                    continue
                if normDict[text][icd10] > bestFreq:
                    bestFreq = normDict[text][icd10]
                    bestICD = icd10
            bestName = ""
            if bestICD in namesDict:
                bestName = namesDict[bestICD]
            if bestICD != '<NONE>' and bestICD != '':
                try:
                    output.write(text + "\t" + bestICD + "\t" + str(bestFreq) + "\t" + str(allFreq) + "\t" + bestName + "\n")
                except UnicodeEncodeError as e:
                    pass
        output.close()

        print("Total entities: " + str(totalEnts) + " normalisations:" + str(totalNorms))
