from recommendation.classifiers.hypertension.hypertensionClassifier import HyperTensionClassifier
from recommendation.classifiers.lipids.lipids import LipidClassifier
from recommendation.dataExtractors.MedicalDataRepository import DataMissing
from recommendation.processStep.ProcessStep import ProcessStep


class GenerateRecommendations(ProcessStep):

    def getStepIdentification(self):
        return "GenerateRecommendations"

    def perform(self, payload) -> None:
        payload.status = "GenerateRecommendations"
        hypertension = HyperTensionClassifier(payload)
        lipids = LipidClassifier(payload, hypertension.patientData)
        try:
            hypertension.classify()
            lipids.classify()
        except DataMissing as ex:
            pass
        # warnings.warn("Data Missing: " + str(payload.diagnosis.addtionalDataRequired))
