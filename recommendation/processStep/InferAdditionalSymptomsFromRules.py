import re

from recommendation.dataExtractors.dataDefinitions import additionalSymptomsDetectionRules, dataDefinitionEntries
from recommendation.payload.patient_data import Payload
from recommendation.processStep.ExtractDataFromText import addBasedOnData
from recommendation.processStep.ProcessStep import ProcessStep


class InferAdditionalSymptomsFromRules(ProcessStep):

    def getStepIdentification(self):
        return "InferAdditionalSymptomsFromRules"

    def perform(self, payload: Payload) -> None:
        payload.status = "InferAdditionalSymptomsFromRules"
        medicalData = payload.patient.medicalData
        abnormalData = ""

        for key in additionalSymptomsDetectionRules.keys():
            try:
                entry = additionalSymptomsDetectionRules[key].replace(" ", "")
                r = re.compile("(?P<parameter>[ęąłóżźćA-Za-z0-9]+)(?P<oper>==|<=|>=|<|>)(?P<value>[0-9]+|True|False)(?P<unit>[a-zA-Z]*[^)\"]*)")
                for rule in [m.groupdict() for m in r.finditer(entry)]:
                    parameter = rule["parameter"]
                    oper = rule["oper"]
                    value = rule["value"]
                    unit = rule["unit"]
                    value = performNormalisation(oper, value, unit)
                    if parameter in medicalData:
                        entry = entry.replace(parameter + oper + value + unit, str(float(medicalData[parameter])) + oper + value)
                    else:
                        entry = entry.replace(parameter + oper + value + unit, "False")
                result = eval(entry)
                if key in medicalData:
                    print("WARNING: data computed via rules was already known:" + key + " value in medicalData: " + str(medicalData[key]) + " value computed:" + str(result))
                else:
                    medicalData[key] = result
                if result:
                    try:
                        addBasedOnData(payload, key, result)
                        abnormalData += " <li>" + dataDefinitionEntries[key][1] + " <b>(" + additionalSymptomsDetectionRules[key] + ")</b></li>"
                    except:
                        print("rule key " + key + " not present in data definitions")
            except BaseException as err:
                print("ERROR additionalSymptomsDetectionRules" + str(err))
        if abnormalData != "":
            payload.abnormalResults = payload.abnormalResults.replace("&nbsp;brak<br>", "") + "<ul>" + abnormalData + "</ul>"


def performNormalisation(oper, value, unit):
    return value
