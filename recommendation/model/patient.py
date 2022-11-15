import json


class Patient(object):
    def __init__(self, serialised) -> None:
        self.patientIdentifier = None
        self.dateAdded = None
        self.annotations = []
        self.medicalInterviewTexts = {}
        self.interviews = []
        self.treatmentPlans = []
        self.medicalData = {}
        self.__dict__ = json.loads(serialised)
