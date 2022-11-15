import re

from recommendation.aux.service.TraceLog import TraceLog
from recommendation.dataExtractors.dataDefinitions import dataDefinitionEntries
from recommendation.payload.patient_data import Payload


class DataMissing(Exception):
    pass


class MedicalDataRepository(object):
    payload: Payload

    def __init__(self, payload) -> None:
        self.payload = payload

    def getEntryFromMedicalData(self, datum: str, stopIfNoData):
        md = self.payload.patient.medicalData
        if dataExists(md, datum):
            value = None
            if datum not in dataDefinitionEntries or dataDefinitionEntries[datum][2] == "boolean":
                value = 1 if (datum in md and (md[datum] == "1" or md[datum] == "true" or md[datum] == True or md[datum] == 1)) else 0

            else:
                value = md[datum]
            dataDef = getDataDef(datum)
            dataDef["value"] = self.convertForOutput(value, dataDef)

            dataDef["title"] = re.sub(r'\|[ ]*$', '', dataDef["title"]).strip()
            if dataDef["type"] == "scalar":
                dataDef["unit"] = re.sub(r'\|.*', '', dataDef["unit"])
                try:
                    val = float(dataDef["value"].replace(",", "."))
                except:
                    dataDef["value"] = -1
                    data_required = self.payload.diagnosis.addtionalDataRequired
                    dataDef = getDataDef(datum)
                    if stopIfNoData and not data_required.__contains__(dataDef):
                        data_required.append(dataDef)
                        TraceLog().add(self.payload.patient.patientIdentifier, "Indispensable data missing: " + datum)
                    if stopIfNoData:
                        self.payload.diagnosis.dataWasSufficient = False
            if dataDef["code"] not in self.payload.basedOnKeys:
                self.payload.diagnosis.basedOnData.append(dataDef)
                self.payload.basedOnKeys.append(dataDef["code"])
            return value
        else:
            data_required = self.payload.diagnosis.addtionalDataRequired
            dataDef = getDataDef(datum)
            if stopIfNoData and not data_required.__contains__(dataDef) and not datum == "plec":
                data_required.append(dataDef)
                TraceLog().add(self.payload.patient.patientIdentifier, "Indispensable data missing: " + datum)
            if stopIfNoData:
                self.payload.diagnosis.dataWasSufficient = False
            return -1

    def convertForOutput(self, value, dataDef):
        if dataDef["type"] == "boolean":
            return str(value) in {"true", "1"}
        if dataDef["type"] == "text" and dataDef["code"] == "plec":
            return "FEMALE" if str(value) in {"FEMALE", "żeńska"} else "MALE"
        return value

    def getIndispensableMedicalEntry(self, datum: str):
        return self.getEntryFromMedicalData(datum, True)

    def getOptionalMedicalEntry(self, datum: str):
        return self.getEntryFromMedicalData(datum, False)


def nodata(map, entry):
    return not dataExists(map, entry)


def dataExists(map, entry):
    return map.__contains__(entry) and map[entry] != None


def getDataDef(datum):
    if dataDefinitionEntries.__contains__(datum):
        dataDef = dataDefinitionEntries[datum]
    else:
        dataDef = [datum, datum.replace("_", " "), "boolean", ""]
    return getDataDefObject(dataDef)


def getDataDefIfExists(datum):
    if dataDefinitionEntries.__contains__(datum):
        dataDef = dataDefinitionEntries[datum]
        return getDataDefObject(dataDef)
    else:
        return None


def getDataDefObject(dataDef):
    units = dataDef[3].split("|")
    unitsJoined = "|".join(map(lambda x: x.strip(), units))
    unitsStrippedOfFormulas = re.sub(r'\([^)]*\)', '', unitsJoined)
    unitsStrippedOfNorms = re.sub(r'\{[^}]*\}', '', unitsStrippedOfFormulas)
    return buildDefObject(dataDef[0], dataDef[1], dataDef[2], unitsStrippedOfNorms)


def buildDefObject(code, title, type, unitsStrippedOfNorms):
    return {"code": code,
            "title": title,
            "type": type,
            "unit": unitsStrippedOfNorms}
