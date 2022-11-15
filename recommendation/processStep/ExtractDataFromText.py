import re

from recommendation.dataExtractors.MedicalDataRepository import nodata, getDataDef, buildDefObject
from recommendation.dataExtractors.dataDefinitions import dataDefinitionEntries
from recommendation.dataExtractors.dataMap import textDataRegexMap
from recommendation.processStep.ProcessStep import ProcessStep


class ExtractDataFromText(ProcessStep):

    def getStepIdentification(self):
        return "ExtractDataFromText"

    def perform(self, payload) -> None:
        payload.status = "ExtractDataFromText"

        for text in payload.texts:
            for entry in textDataRegexMap:
                if nodata(payload.patient.medicalData, entry):
                    recipe = textDataRegexMap[entry]
                    patterns = recipe["regex"]
                    if not isinstance(patterns, list):
                        patterns = [patterns]
                    for pattern in patterns:
                        if nodata(payload.patient.medicalData, entry):
                            if recipe["type"] == "simple":
                                searchItem = re.search(pattern, text)
                                if searchItem != None:
                                    payload.patient.medicalData[entry] = searchItem.group(1).strip()
                            if recipe["type"] == "exists":
                                searchItem = re.search(pattern, text)
                                payload.patient.medicalData[entry] = 1 if searchItem != None else -1
            k = ""
            try:
                for key in dataDefinitionEntries:
                    k = key
                    entry = dataDefinitionEntries[key]
                    #     "eGFR": ["eGFR", "eGFR (estimated glomerular filtration rate)", "scalar", "ml/min/1,73 m2 {norm: M[19,inf):[90,130),F[19,inf):[90,120),d[0,8):[26,56],d[8,56):[41,91],d[56,365):[74,118],[1,13):[106,160],M[13,19):[110,170],F[13,19):[104,148]}"],
                    if entry[2] == "scalar":
                        unitDefinitions = dataDefinitionEntries[key][3]
                        unitsStrippedOfNorms = re.sub(r'\{[^}]*\}', '', unitDefinitions)
                        standardUnit = re.sub(r'\|.*', '', unitsStrippedOfNorms).strip()
                        pattern = "(" + entry[1] + ")[0-9a-zA-Z,.]{0,50}[: ]{0,5}([0-9,. ]+)[\[\(]{0,1}" + standardUnit
                        searchItem = re.search(pattern, text)
                        if searchItem != None:
                            payload.patient.medicalData[entry] = searchItem.group(2).strip()
            except:
                print("ERROR: while getting generic patterns of: " + k)


class ExtractAdditionalDataFromText():

    def __init__(self, payload, patientData) -> None:
        self.patientData = patientData
        self.payload = payload

    def checkAdHocText(self, pattern) -> int:
        value = -1
        if nodata(self.payload.patient.medicalData, pattern):
            for text in self.payload.texts:
                searchItemPos = text.find(pattern)
                if searchItemPos != -1:
                    value = 1
        self.payload.patient.medicalData[pattern] = value

        if value == 1:
            addBasedOnData(self.payload, pattern, True)
        return value

    def checkAdHocTextR(self, pattern, key) -> int:
        value = -1
        if nodata(self.payload.patient.medicalData, key):
            for text in self.payload.texts:
                searchItem = re.search(pattern, text)
                if searchItem != None:
                    value = 1
        self.payload.patient.medicalData[key] = value
        if value == 1:
            addBasedOnData(self.payload, key, True)
        return value

    def getAdHocValueR(self, pattern, key) -> float:
        value = -1
        if nodata(self.payload.patient.medicalData, key):
            for text in self.payload.texts:
                searchItem = re.search(pattern, text)
                if searchItem != None:
                    try:
                        value = float(searchItem.group(1).strip().replace(",", "."))
                    except:
                        pass
        self.payload.patient.medicalData[key] = value
        if value != -1:
            addBasedOnData(self.payload, key, value)
        return value


def addBasedOnData(payload, key, value):
    dataDef = getDataDef(key)
    if dataDef == None:
        dataDef = buildDefObject(key, key, "boolean", " ")
    dataDef["value"] = value

    if dataDef["code"] not in payload.basedOnKeys:
        payload.diagnosis.basedOnData.append(dataDef)
        payload.basedOnKeys.append(dataDef["code"])
