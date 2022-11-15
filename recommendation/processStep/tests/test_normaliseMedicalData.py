from unittest import TestCase

from recommendation.model.patient import Patient
from recommendation.payload.patient_data import Payload
from recommendation.processStep.NormaliseMedicalDataUnits import NormaliseMedicalDataUnits


class TestNormaliseMedicalDataUnits(TestCase):
    def test_convert_datum(self):
        payload = Payload()
        patient = Patient("{}")
        patient.patientIdentifier = 0
        payload.patient = patient

        n = NormaliseMedicalDataUnits(payload)
        for key in medicalData:
            medicalDatum = medicalData[key]
            newval = n.convertDatum(key, medicalDatum[0]["value"], medicalDatum[0]["unit"])
            self.assertEqual(newval, expected[key])


expected = {
    "neutrofile": "10",

    "eGFR": "10",

    "cholesterol_calkowity": "0.2586",

    "LDL": "600.47",

    "hemoglobina": "100.7",

    "plec": "męska",

    "wiek": "42525"
}
medicalData = {
    "neutrofile": [{
        "date": "2020-11-10T17:59:55.656714",
        "value": "10",
        "unit": "tys/µl"
    }],
    "eGFR": [{
        "date": "2020-11-10T17:59:55.6452",
        "value": "10",
        "unit": "ml/min"
    }],
    "cholesterol_calkowity": [{
        "date": "2020-11-10T17:59:55.60924",
        "value": "10",
        "unit": "mmol/l "
    }],
    "LDL": [{
        "date": "2020-11-10T17:59:55.656401",
        "value": "10",
        "unit": "mmol/l "
    }],
    "hemoglobina": [{
        "date": "2020-11-10T17:59:55.656414",
        "value": "10",
        "unit": "% "
    }, {
        "date": "2020-11-10T17:59:55.656388",
        "value": "10",
        "unit": "mmol/l "
    }, {
        "date": "2020-11-10T17:59:55.661072",
        "value": "10",
        "unit": "g/dl"
    }],
    "plec": [{
        "date": "2020-11-10T17:59:57.726537",
        "value": "męska",
        "unit": "żeńska/męska"
    }],
    "wiek": [{
        "date": "2020-11-10T17:59:57.726566",
        "value": "42525",
        "unit": "wiek w DNIACH"
    }]
}
