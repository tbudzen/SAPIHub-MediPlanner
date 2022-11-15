from unittest import TestCase

from recommendation.model.patient import Patient
from recommendation.payload.patient_data import Payload
from recommendation.processStep.InferAdditionalSymptomsFromRules import InferAdditionalSymptomsFromRules


class TestInferAdditionalSymptomsFromRules(TestCase):
    def test_perform(self):
        t = InferAdditionalSymptomsFromRules()
        payload = Payload()
        payload.patient = Patient("{}")
        payload.patient.medicalData = {"tętno": "200", "eGFR":"70", 'tachykardia': "True"}
        t.perform(payload)
        print(payload.abnormalResults)
        print(str(payload.patient.medicalData))
