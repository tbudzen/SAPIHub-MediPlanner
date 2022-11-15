import time

import spacy

from actually_working_nlp_processor.attributes.ann_model import AnnProcessor
from actually_working_nlp_processor.attributes.attributes import Attributes
from actually_working_nlp_processor.conf import NLP_ROOT
from actually_working_nlp_processor.crf.conversion.crfconversion import CrfConversion
from actually_working_nlp_processor.crf.crfAbstract.CrfAbstract import CrfAbstract, fileToStr
from actually_working_nlp_processor.crf.deconversion.deconversion import Deconversion
from actually_working_nlp_processor.normalisation.basic.normalise import Normalisation
from actually_working_nlp_processor.normalisation.createDictionary import DictionaryCreation
from actually_working_nlp_processor.relations.myrelations import TheRelations


class NLPProcessor():

    def __init__(self, nlp):
        self.nlp = nlp
        self.crfConversion = CrfConversion(nlp)
        self.deconversion = Deconversion()
        self.dc = DictionaryCreation(nlp)
        self.crfAbstract = CrfAbstract()
        self.attributes = Attributes()
        self.normalisation = Normalisation(nlp)
        self.relations = TheRelations(nlp)
        self.annProcessor = AnnProcessor(NLP_ROOT + "attributes/status_rfc.sav",
                                         NLP_ROOT + "attributes/status_bc.sav",
                                         NLP_ROOT + "attributes/status_bc_date.sav",
                                         NLP_ROOT + "attributes/source_bc.sav")

    def log(self, param):
        print(param)

    def process_text(self, text, age, gender) -> str:
        time_1 = time.time()
        ann_names_crf = self.names_detection_process(text)
        print("Time of name detection  = " + str( time.time() - time_1) + " [s]")
        time_1 = time.time()
        normalised = self.normalisation_process(text, ann_names_crf) + ann_names_crf
        print("Time of normalisation_process  = " + str(time.time() - time_1) + " [s]")
        time_1 = time.time()
        relations = self.relations_process(text, normalised)
        print("Time of relations_process  = " + str(time.time() - time_1) + " [s]")
        time_1 = time.time()
        return self.attributes_process(relations, text, age, gender)

    def names_detection_process(self, text) -> str:
        print('    Names detection processing...')
        crfFeatures = self.crfConversion.my_conversion(text, False)
        crfNames = self.crfAbstract.crfTest(crfFeatures)
        ann = self.deconversion.deconversion(crfNames)
        return ann

    def normalisation_process(self, text, ann_names_crf):
        print('    Normalisation processing...')
        ann_names_crf = self.attributes.strip_annotations(ann_names_crf, "N")
        return self.normalisation.normalise(text, ann_names_crf, NLP_ROOT + "normalisation/dict.tsv")

    def relations_process(self, text: str, normalised: str) -> str:
        print('    Relations processing...')
        stripped = self.attributes.strip_annotations(normalised, "R")
        return self.relations.process_relations(text, stripped)

    def attributes_process(self, relations: str, text: str, age, sex) -> str:
        self.attributes.strip_annotations(relations, 'A')

        return self.annProcessor.annotate(text, relations, age, sex)


if __name__ == '__main__':
    print("Loading pl_spacy_model for the processor...")
    nlp = spacy.load('pl_spacy_model')
    print("pl_spacy_model loaded.")
    nlpProcessor = NLPProcessor(nlp)
    print("result 1:...")
    time_1 = time.time()
    result = (nlpProcessor.process_text(fileToStr(NLP_ROOT + "testInput/patient.txt"), 60, "1"))
    time_2 = time.time()
    print(result)
    print("Time of name detection  = " + str(time_2 - time_1) + " [s]")
