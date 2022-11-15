from recommendation.processStep.ExtractDataFromAnnotations import ExtractDataFromAnnotations
from recommendation.processStep.ExtractDataFromText import ExtractDataFromText
from recommendation.processStep.FetchPatientDataFromDB import FetchPatientDataFromDB
from recommendation.processStep.GenerateAnnotations import GenerateAnnotations
from recommendation.processStep.GenerateEpicrisis import GenerateEpicrisis
from recommendation.processStep.GenerateRecommendations import GenerateRecommendations
from recommendation.processStep.GetDataOutOfNorms import GetDataOutOfNorms
from recommendation.processStep.InferAdditionalSymptomsFromRules import InferAdditionalSymptomsFromRules
from recommendation.processStep.IsolateData import IsolateData
from recommendation.processStep.NormaliseMedicalDataUnits import NormaliseMedicalDataUnits


class ProcessPerformer(object):

    def __init__(self) -> None:
        self._processChain = [GenerateAnnotations(), #1
                              NormaliseMedicalDataUnits(),
                              FetchPatientDataFromDB(), #3
                              ExtractDataFromAnnotations(),
                              ExtractDataFromText(), #5
                              IsolateData(), #6
                              GetDataOutOfNorms(), #7
                              InferAdditionalSymptomsFromRules(),
                              GenerateRecommendations(), #9
                              GenerateEpicrisis()]

    def setPayload(self, payload):
        self._payload = payload

    def start(self) -> None:
        for step in self._processChain:
            if (self._payload.diagnosis.dataWasSufficient):
                step.logStart(self._payload)
                step.perform(self._payload)
                step.logFinished(self._payload)
