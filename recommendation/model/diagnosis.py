class Diagnosis(object):
    def __init__(self) -> None:
        self.patientIdentifier = None
        self.date = None
        self.analyserVersion = None
        self.manualDiagnosis = ""
        self.additionalManualComment = None
        self.diagnoses = []
        self.addtionalDataRequired = []
        self.basedOnData = []
        self.dataWasSufficient = True
