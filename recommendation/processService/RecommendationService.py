from datetime import date

from recommendation.model.patient import Patient
from recommendation.model.recommendationOutput import RecommendationOutput
from recommendation.model.treatment_plan import TreatmentPlan
from recommendation.payload.patient_data import Payload
from recommendation.processService.ProcessPerformer import ProcessPerformer


class RecommendationService(object):

    def __init__(self) -> None:
        self.performer = ProcessPerformer()

    def generate_recommendation(self, patient: Patient) -> RecommendationOutput:
        payload = Payload()
        payload.patient = patient
        payload.texts = patient.medicalInterviewTexts
        self.performer.setPayload(payload)
        self.performer.start()
        diagnosis = payload.diagnosis
        diagnosis.analyserVersion = "1.0"
        diagnosis.date = date.today().isoformat()
        diagnosis.diagnoses = payload.icdCodes
        diagnosis.patientIdentifier = patient.patientIdentifier
        plan = TreatmentPlan()
        plan.treatment = payload.treatment_plan
        plan.epicrisis = payload.epicrisis
        # brat- trained anotations not sufficiently precise... to be delicate. Hence skipping:
        # plan.drugsPrescribed = payload.drugsPrescribed
        plan.date = date.today().isoformat()
        plan.patientIdentifier = payload.patient.patientIdentifier
        out = RecommendationOutput()
        out.diagnosis = diagnosis
        out.treatmentPlan = plan
        return out
