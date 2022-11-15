from recommendation.model.PatientData import PatientData
from recommendation.model.diagnosis import Diagnosis
from recommendation.model.patient import Patient


class Payload(object):
    def __init__(self) -> None:
        self.annotations = []  #:Annotation
        self.annotationsGen = []  #:Annotation
        self.diagnosis: Diagnosis = Diagnosis()
        self.patient: Patient = None
        self.texts = []
        self.risk = []
        self.treatment_plan = ""  # TreatmentPlan = TreatmentPlan()
        self.epicrisis = ""
        self.status = "INIT"
        self.basedOnKeys = []
        self.icdCodes = []
        self.drugsPrescribed = []
        self.abnormalResults = ""
        self.patientData=PatientData()

    def get_status(self) -> str:
        return self.status

    # def get_recommendation(self) -> str:
    #     if self.diagnosis.dataWasSufficient:
    #         return "diagnosis: " + self.diagnosis.manualDiagnosis + "treatment plan:" + self.treatment_plan
    #     else:
    #         return "data required:" + ''.join(self.diagnosis.addtionalDataRequired)
