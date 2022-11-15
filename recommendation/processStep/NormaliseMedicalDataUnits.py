import re

from recommendation.aux.service.TraceLog import TraceLog
from recommendation.dataExtractors.dataDefinitions import dataDefinitionEntries
from recommendation.processStep.ProcessStep import ProcessStep


class NormaliseMedicalDataUnits(ProcessStep):

    def getStepIdentification(self):
        return "NormaliseMedicalDataUnits"

    def perform(self, payload) -> None:
        payload.status = "NormaliseMedicalDataUnits"
        medicalData = payload.patient.medicalData
        payload.patient.medicalDataArrays = {}
        for key in medicalData:
            medicalDatum = medicalData[key]
            # retain result arrays
            payload.patient.medicalDataArrays[key] = medicalDatum
            # add unit conversion
            try:
                medicalData[key] = self.convertDatum(payload, key, medicalDatum[-1]["value"], medicalDatum[-1]["unit"])
            except:
                pass

    def convertDatum(self, payload, key, value, unit):
        unit = unit.strip()
        try:
            unitDefinitions = dataDefinitionEntries[key][3]
            unitsStrippedOfNorms = re.sub(r'\{[^}]*\}', '', unitDefinitions)
            standardUnit = re.sub(r'\|.*', '', unitsStrippedOfNorms).strip()
            if unit == standardUnit:
                return value
            else:
                formulas = self.getFormulas(key)
                return self.convertValue(value, unit, standardUnit, formulas[unit])
        except BaseException as err:
            print("Meta of data calculation warning: " + key + " " + value + " " + unit + "err:" + str(err))
            TraceLog().add(payload.patient.patientIdentifier, "Meta of data calculation warning, normalisation formulas to be revisited for: " + key + " " + value + " " + unit)
            return value

    def getFormulas(self, datumCode):
        datumDef = dataDefinitionEntries[datumCode]
        # map unit -> formula (first get the unit name, stripped of formulas and norms, then the formula itself and generate map
        try:
            return dict(map(
                lambda x: (re.sub(r'\([^)]*\)', '', re.sub(r'\{[^}]*\}', '', x)).strip(),
                           re.search("[^(]*\(([^)]*)\).*", x).group(1).strip() if "(" in x else ""
                           ),
                datumDef[3].split("|")))
        except:
            print("Bad meta definition:" + str(datumDef))
            raise

    def convertValue(self, value, fromUnit, toUnit, formula):
        formula = re.sub(r'[ ()]', '', formula)
        if "mm:" in formula:
            mm = float(re.search("\d[\d,.]*", formula).group(0).replace(",", "."))
            return str(mm * float(value) / 10)
        else:
            return str(eval(str(value) + formula.replace(",", ".")))
