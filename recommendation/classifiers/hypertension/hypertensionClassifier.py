from recommendation.classifiers.MedicalDataMapper import MedicalDataMapper
from recommendation.classifiers.hypertension.hypertensionDiagnosis import HypertensionDiagnosis
from recommendation.classifiers.hypertension.hypertensionTreatmentPlan import HypertensionTreatmentPlan
from recommendation.dataExtractors.MedicalDataRepository import MedicalDataRepository, DataMissing
from recommendation.model.PatientData import PatientData
from recommendation.payload.patient_data import Payload


class HyperTensionClassifier(MedicalDataRepository):

    def __init__(self, payload:Payload) -> None:
        self.patientData = payload.patientData
        super().__init__(payload)

    def classify(self):
        # -1 niezainicjowane zmienna (nie znaleziono informacji o tej chorobie lub jej braku)
        # 0 brak choroby/symptomu
        # 1 jest choroba
        # inna wartość dodatnia - wartość właściwa dla danego badania

        # extract common data

        if not self.payload.diagnosis.dataWasSufficient:
            raise DataMissing("")
        # generate diagnosis
        HypertensionDiagnosis(self.payload, self.patientData).generateDiagnosis()

        # generate treatment plan
        hypertensionTreatmentPlanService = HypertensionTreatmentPlan(self.payload, self.patientData)
        hypertensionTreatmentPlanService.generateTreatmentPlan()

        # generate contradindications
        hypertensionTreatmentPlanService.generateContraindications()
