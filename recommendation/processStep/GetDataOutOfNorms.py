import re

from recommendation.aux.service.TraceLog import TraceLog
from recommendation.dataExtractors.dataDefinitions import dataDefinitionEntries
from recommendation.payload.patient_data import Payload
from recommendation.processStep.ProcessStep import ProcessStep


class GetDataOutOfNorms(ProcessStep):

    def getStepIdentification(self):
        return "GetDataOutOfNorms"

    def perform(self, payload: Payload) -> None:
        payload.status = "GetDataOutOfNorms"
        medicalData = payload.patient.medicalData
        payload.patient.medicalDataArrays = {}
        abnormalData = ""
        for key in medicalData:
            medicalDatum = medicalData[key]
            try:
                unitDefinitions = dataDefinitionEntries[key][3]
                age_in_days = payload.patientData.age_in_days
                gender = "F" if payload.patientData.plec == 1 else "M"
                centile = payload.patientData.centile
                age_in_years = int(age_in_days / 365)
                value_ = float(medicalDatum.replace(",", "."))
                type = dataDefinitionEntries[key][2]
                if (type == "scalar"):
                    try:
                        notInNorms, norm = self.valueNotInNorms(age_in_days, age_in_years, gender, centile, unitDefinitions, value_)
                        if notInNorms:
                            unitsStrippedOfNorms = re.sub(r'\{[^}]*\}', '', unitDefinitions)
                            standardUnit = re.sub(r'\|.*', '', unitsStrippedOfNorms).strip()
                            normStr = "dla " + norm["sex"].replace("M", " &male; ").replace("F", " &female; ") + ", wieku" + norm["inDays"].replace("d", " (dni)") + ": " + norm["frombr"] + norm["from"] + "," + norm["to"].replace("1279000000", "&infin;") + norm["tobr"] + " zakres: " + norm["fromvbr"] + norm["fromv"] + "," + norm["tov"].replace("1279000000", "&infin;") + norm["tovbr"]
                            if norm["centiles"] != None:
                                normStr = normStr + " , centyli: " + norm["fromcbr"] + norm["fromc"] + "," + norm["toc"] + norm["tocbr"]
                            abnormalData += " <li>" + dataDefinitionEntries[key][1] + ": <b>" + str(value_) + "</b> " + standardUnit + "&nbsp; norma: " + normStr + "</li>"
                    except:
                        TraceLog().add(payload.patient.patientIdentifier, "Norm definition error: key" + key + " value:" + str(value_) + " unitDefinition with norms:" + unitDefinitions + " ")
            except:
                pass
        payload.abnormalResults = "<br><b>Wyniki poza normą:</b>"
        if (abnormalData.strip() != ""):
            payload.abnormalResults += "<ul>" + abnormalData + "</ul>"
        else:
            payload.abnormalResults += "&nbsp;brak<br>"

    def valueNotInNorms(self, age_in_days, age_in_years, gender, centile, unitDefinitions, value):
        # {norm: M[15,inf):[0,40),  F[15,inf):[0,35), d[0,22):[0,130], d[22,61):[4,120], Md[61,365):[5,65], Fd[61,365):[5,35], [1,15):[0,23],}
        fullNormSection = re.search('{norm:([^}]*)}', unitDefinitions)
        if (fullNormSection != None):
            normsection = fullNormSection.group(1)
            norms = normsection.strip().replace("inf", "1279000000")
            r = re.compile("(?P<sex>[FM]*)(?P<inDays>[d]*)(?P<frombr>[\[(])(?P<from>[^,]+),(?P<to>[^\])]+)(?P<tobr>[\])])((?P<centiles>[c]*)(?P<fromcbr>[\[(])(?P<fromc>[^,]+),(?P<toc>[^\])]+)(?P<tocbr>[\])])){0,1}:(?P<fromvbr>[\[(])(?P<fromv>[^,]+),(?P<tov>[^\])]+)(?P<tovbr>[\])])(?P<unit><.*>){0,1}")
            for normEntry in [m.groupdict() for m in r.finditer(norms)]:
                genderFits = normEntry["sex"] == "" or normEntry["sex"] == gender

                ageInDays = not (normEntry["inDays"] == "" or normEntry["inDays"] == "")
                fromTime = float(normEntry["from"])
                toTime = float(normEntry["to"])
                fromEq = normEntry["frombr"] == "["
                toEq = normEntry["tobr"] == "]"
                timeMeasure = age_in_days if ageInDays else age_in_years
                ageFits = self.isInRange(fromEq, fromTime, timeMeasure, toEq, toTime)

                fromV = float(normEntry["fromv"])
                toV = float(normEntry["tov"])
                fromvEq = normEntry["fromvbr"] == "["
                tovEq = normEntry["tovbr"] == "]"
                valueFits = self.isInRange(fromvEq, fromV, value, tovEq, toV)

                if normEntry["centiles"] == None or normEntry["centiles"] == "" or centile == -1 or centile == None:
                    centilesOk = True
                else:
                    fromV = float(normEntry["fromc"])
                    toV = float(normEntry["toc"])
                    fromvEq = normEntry["fromcbr"] == "["
                    tovEq = normEntry["tocbr"] == "]"
                    centilesOk = self.isInRange(fromvEq, fromV, centile, tovEq, toV)

                if (genderFits and ageFits and centilesOk):
                    print(normEntry)
                    return (not valueFits, normEntry)
            return (False, None)
        else:
            # no norm clause
            return (None, None)

    def isInRange(self, fromEq, fromV, value, toEq, toV):
        return (fromEq and fromV == value or fromV < value < toV or toEq and toV == value)
