# https://pl.wikipedia.org/wiki/Skala_HAS-BLED
# https://docs.google.com/document/d/1ZmHmr6CDJMU5bTAuFiVVxAnPSx_AY9Aw1r1wtukjXrY/edit
from recommendation.classifiers.MedicalDataMapper import MedicalDataMapper
from recommendation.processStep.ExtractDataFromText import ExtractAdditionalDataFromText


class KDIGO(object):

    def __init__(self, payload, patientData) -> None:
        self.extractor = MedicalDataMapper(payload)
        self.patientData = patientData
        self.payload = payload
        self.dataFromText = ExtractAdditionalDataFromText(payload, patientData)

    def calculateFromPatientData(self):

        score = 0
        source = []
        eGFR = self.patientData.eGFR

        if (eGFR > 90):
            score = "G1"
            source.append("eGFR > 90")

        elif (eGFR >= 60):
            score = "G2"
            source.append("60 <= eGFR < 90")

        elif (eGFR >= 45):
            score = "G3a"
            source.append("45 <= eGFR < 60")

        elif (eGFR >= 30):
            score = "G3b"
            source.append("30 <= eGFR < 45")

        elif (eGFR >= 15):
            score = "G4"
            source.append("14 <= eGFR < 30")
        elif (eGFR > -1 and eGFR < 15):
            score = "G5"
            source.append("eGFR < 15")

        return score, source
