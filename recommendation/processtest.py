import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from recommendation.model.patient import Patient
from recommendation.processService.RecommendationService import RecommendationService


def getPipelineOutput():
    annotations = []
    with open("recommendation/dataSources/annotationData/data3_patient_" + str(
            patient.patientIdentifier) + ".json") as json_file:
        annotation = json.load(json_file)
    annotations.append(annotation)
    return annotations


if __name__ == "__main__":
    patient = Patient()
    patient.patientIdentifier = 349003
    patient.annotations = getPipelineOutput()

    output = RecommendationService().generate_recommendation(patient)

    diagnosis = output.diagnosis
    treatmentPlan = output.treatmentPlan

    print(diagnosis.manualDiagnosis)
    print(treatmentPlan.treatment)
