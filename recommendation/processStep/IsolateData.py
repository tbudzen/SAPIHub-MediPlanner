from recommendation.classifiers.MedicalDataMapper import MedicalDataMapper
from recommendation.payload.patient_data import Payload
from recommendation.processStep.ProcessStep import ProcessStep


class IsolateData(ProcessStep):

    def getStepIdentification(self):
        return "IsolateData"

    def perform(self, payload: Payload) -> None:
        payload.status = "IsolateData"
        dataExtractorImpl = MedicalDataMapper(payload)
        dataExtractorImpl.isolateData()
        dataExtractorImpl.isolateContraindicationsData()
