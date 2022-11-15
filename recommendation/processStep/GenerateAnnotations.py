import spacy

from actually_working_nlp_processor.nlp_processor import NLPProcessor
from recommendation.aux.service.TraceLog import TraceLog
from recommendation.dataExtractors.PeselDataExtractor import PeselDataExtractor
from recommendation.processStep.ProcessStep import ProcessStep


class GenerateAnnotations(ProcessStep):

    def getStepIdentification(self):
        return "GenerateAnnotations"

    def __init__(self):
        nlp = spacy.load('pl_spacy_model')
        print("pl_spacy_model loaded.")
        self.nlpProcessor = NLPProcessor(nlp)

    def perform(self, payload) -> None:
        payload.status = "GenerateAnnotations"
        processedtexts = []
        for text in payload.texts:
            if (text != None and len(text) > 1 and not text in processedtexts):
                processedtexts.append(text)
                TraceLog().add(payload.patient.patientIdentifier, "Text length: " + (str(len(text)) if text != None else "None"))
                annotations = self.generateAnnotations(payload, text)
                TraceLog().add(payload.patient.patientIdentifier, "Ann: " + (str(annotations.count('\n')) if annotations != None else "N"))
                if annotations != None and ''.join(annotations.split()) != "":
                    payload.annotationsGen.append(annotations)
                    #   payload.annotationsGen.append("\n")

    def generateAnnotations(self, payload, text):
        sex, years = self.extractInitialData(payload)
        return self.nlpProcessor.process_text(text, years, sex)

    def extractInitialData(self, payload):
        de = PeselDataExtractor()
        gender, ageInDays = de.extractAgeinDaysAndGender(payload.patient.patientIdentifier)
        years = int(ageInDays / 365)
        payload.patient.medicalData["wiek"] = [{"value": str(years), "unit": "wiek w LATACH", "type": "scalar"}]
        payload.patient.medicalData["age_in_days"] = [{"value": str(ageInDays), "unit": "age_in_days", "type": "scalar"}]
        payload.patient.medicalData["plec"] = [{"value": gender, "unit": "męska|żeńska", "type": "text"}]
        sex = "1" if (gender == "FEMALE") else "0"
        return sex, years
