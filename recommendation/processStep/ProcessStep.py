from recommendation.aux.service.TraceLog import TraceLog
from recommendation.payload.patient_data import Payload


class ProcessStep(object):

    def perform(self, payload: Payload):
        raise NotImplementedError

    def logStart(self, payload: Payload):
        TraceLog().add(payload.patient.patientIdentifier, "<b>" + self.getStepIdentification() + " </b>phase started...")

    def logFinished(self, payload: Payload):
        TraceLog().add(payload.patient.patientIdentifier, " ... finished")

    def getStepIdentification(self):
        return "INIT"
