import os
import uuid

from actually_working_nlp_processor.conf import NLP_ROOT

TMP_CRF_FEATURES = NLP_ROOT + "tmp/features_"
TMP_CRF_NAMES = NLP_ROOT + "tmp/names_"


class CrfAbstract():

    def __init__(self):
        self.model = NLP_ROOT + "crf/model/model3_2.m"
        pass

    def crfTest(self, features) -> str:
        hexdigest = str(uuid.uuid4())
        tmpPath = TMP_CRF_FEATURES + hexdigest + ".cfr"
        tmpOutPath = TMP_CRF_NAMES + hexdigest + ".cfr"

        strToFile(features, tmpPath)
        os.system("crf_test -m " + self.model + " " + tmpPath + " > " + tmpOutPath)
        return fileToStr(tmpOutPath)


def fileToStr(tmpOutPath):
    file = open(tmpOutPath)
    cont = file.read()
    file.close()
    return cont


def strToFile(content, tmpPath):
    outF = open(tmpPath, "w", encoding="utf-8", errors='ignore')
    outF.write(content)
    outF.close()
