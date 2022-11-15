import re

from recommendation.dataExtractors.MedicalDataRepository import nodata, getDataDef, buildDefObject
from recommendation.dataExtractors.dataDefinitions import dataDefinitionEntries
from recommendation.dataExtractors.dataMap import annotationAdditionalMap, synonymsMap
from recommendation.payload.patient_data import Payload
from recommendation.processStep.ProcessStep import ProcessStep


class ExtractDataFromAnnotations(ProcessStep):

    def getStepIdentification(self):
        return "ExtractDataFromAnnotations"

    def perform(self, payload) -> None:
        self.extractFromNewAnnotations(payload)
        self.extractFromOldAnnotations(payload)

    def extractFromNewAnnotations(self, payload):
        condtionEntryLike = {}
        references = {}
        drugs = {}
        drugInfoCont = {}
        # relations:
        drugInfoRelation = {}
        negations = {}
        dates = {}
        attributes = {}
        for annotations in payload.annotationsGen:
            print("ANNOTATIONS:")
            # annotations from diff texts - beware of ids
            annotationLines = annotations.splitlines()
            while ("" in annotationLines):
                annotationLines.remove("")
            for line in annotationLines:
                print("annnotation line:" + line)
                r = re.compile("^(?P<type>[TNRA])(?P<id>[\d]+)[\t ]*(?P<typename>[A-Za-z_]+)")
                try:
                    for entry in [m.groupdict() for m in r.finditer(line)]:
                        type = entry["type"]
                        id = entry["id"]
                        fullId = type + id
                        typename = entry["typename"]

                    if typename in ["Condition", "Investigation", "Negation", "Treatment", "Drug", "Drug_dose", "Date", "Symptom"]:
                        pos1, pos2, content = self.extractFromConditionTypeLine(line)
                        if typename in ["Condition", "Investigation", "Treatment", "Symptom"]:
                            condtionEntryLike[fullId] = ({"typename": typename, "content": content})

                        if typename in ["Drug"]:
                            drugs[fullId] = ({"typename": typename, "content": content})

                        if typename in ["Drug_dose"]:
                            drugInfoCont[fullId] = ({"typename": typename, "content": content})

                    elif typename == "Reference":
                        ref, icdCode, content = self.extractFromReference(line)
                        references[fullId] = ({"ref": ref, "icdCode": icdCode, "content": content})
                    elif type == "R":
                        # typename = Neg, Drg, Dat
                        arg1, arg2 = self.extractRelationData(line)
                        if typename in ["Neg"]:
                            negations[fullId] = ({"ref": arg2, "negationPhraseRef": arg1})
                        if typename in ["Drg"]:
                            drugInfoRelation[fullId] = ({"drugId": arg1, "attribRef": arg2})
                        if typename in ["Dat"]:
                            dates[fullId] = ({"dateRef": arg1, "ofRef": arg2})
                    elif type == "A":
                        ref, content = self.extractAttributeData(line)
                        attributes[fullId] = ({"typename": typename, "of": ref, "content": content})
                except:
                    print("ERROR: Annotation parse for: " + line)
            self.joinData(condtionEntryLike, references, drugs, drugInfoRelation, negations, drugInfoCont, dates, attributes)
            self.addDataFromAnnotations(payload, condtionEntryLike, references, drugs, drugInfoRelation, negations, drugInfoCont, dates, attributes)

    def joinData(self, condtionEntryLike, references, drugs, drugInfoRelation, negations, drugInfoCont, dates, attributes):
        for key, negation in negations.items():
            if negation["ref"] in condtionEntryLike:
                condtionEntryLike[negation["ref"]]["negated"] = True
            else:
                print("ERROR: negation of emptyness, key: " + key)

            # references[fullId] = ({"ref": ref, "icdCode": icdCode, "content": content})
        for key, reference in references.items():
            if reference["ref"] in condtionEntryLike:
                condtionEntryLike[reference["ref"]]["detail"] = "ICD-10: " + reference["icdCode"] + " (" + reference["content"] + ") "
                condtionEntryLike[reference["ref"]]["icdCode"] = reference["icdCode"]
                condtionEntryLike[reference["ref"]]["classification"] = reference["content"]
            else:
                print("ERROR: ref of emptyness, key: " + key)
            # drugInfo[fullId] = ({"drugId": arg1, "attribRef": arg2})
        for key, entry in drugInfoRelation.items():
            if entry["drugId"] in drugs and entry["attribRef"] in drugInfoCont:
                drugs[entry["drugId"]]["detail"] = drugInfoCont[entry["attribRef"]]["content"]
            else:
                print("ERROR: ref of drug emptyness, key: " + key)
        # TODO review attributes and decide

    def addDataFromAnnotations(self, payload: Payload, condtionEntryLike, references, drugs, drugInfoRelation, negations, drugInfoCont, dates, attributes):
        negated = False
        comment = ""
        icdCode = ""
        classification = ""
        for key, entry in condtionEntryLike.items():
            try:
                if "negated" in entry:
                    negated = True
                if "detail" in entry:
                    comment = entry["detail"]
                if "classification" in entry:
                    classification = entry["classification"]
                if "icdCode" in entry:
                    icdCode = entry["icdCode"]

                self.addBasedOnData(payload, entry["content"], not negated, comment, classification, icdCode)
            except:
                print("ERROR: while adding data from ann.  " + key + " : " + str(entry))

        for key, entry in drugs.items():
            detail = ""
            content = ""
            try:
                if "detail" in entry:
                    detail = " (" + entry["detail"] + ")"
                if "content" in entry:
                    content = entry["content"]
                if (content + detail) not in payload.drugsPrescribed:
                    payload.drugsPrescribed.append(content + detail)
            except:
                print("ERROR: while adding data from ann.  " + key + " : " + str(entry))

    def addBasedOnData(self, payload: Payload, key, value, comment, classification, icdCode):
        if icdCode != "":
            if ("ICD-10:" + icdCode) not in payload.icdCodes:
                payload.icdCodes.append("ICD-10:" + icdCode)
            if dataDefinitionEntries.__contains__(classification):
                dataDef = getDataDef(key)
            else:
                dataDef = buildDefObject(classification, classification, "boolean", "ICD-10: " + icdCode)
                # just add in case the Condition phrase fits better the analiser needs
                payload.patient.medicalData[key] = 1 if value else 0
        elif dataDefinitionEntries.__contains__(key):
            dataDef = getDataDef(key)
        else:
            dataDef = buildDefObject(key, key, "boolean", comment)
            payload.patient.medicalData[dataDef["code"]] = 1 if value else 0
        dataDef["value"] = value

        if dataDef["code"] not in payload.basedOnKeys:
            payload.diagnosis.basedOnData.append(dataDef)
            payload.basedOnKeys.append(dataDef["code"])
            if dataDef["type"] == "boolean":
                payload.patient.medicalData[dataDef["code"]] = 1 if value else 0
            elif dataDef["type"] == "scalar":
                print("WARNING - data of scalar type not taken from annot.")
        # print("ann based data added:" + key)

    def extractAttributeData(self, line):
        ref = ""
        content = ""
        try:
            rc = re.compile("^(?P<type>[TNRA])(?P<id>[\d]+)[\t ]*(?P<typename>[A-Za-z]+)[\t ]*(?P<ref>[TNRA][\d]+)[\t ]*(?P<content>.*)")
            for entry in [m.groupdict() for m in rc.finditer(line)]:
                ref = entry["ref"]
                content = entry["content"]
        except:
            print("ERROR:Annot. Attr error for: " + line)
        return (ref, content)

    def extractRelationData(self, line):
        arg1 = ""
        arg2 = ""
        try:
            rc = re.compile("^(?P<type>[TNRA])(?P<id>[\d]+)[\t ]*(?P<typename>[A-Za-z]+)[\t ]*Arg\d:(?P<arg1>[TNRA][\d]+)[\t ]*Arg\d:(?P<arg2>[TNRA][\d]+)")
            for entry in [m.groupdict() for m in rc.finditer(line)]:
                arg1 = entry["arg1"]
                arg2 = entry["arg2"]
        except:
            print("Relation extraction error for: " + line)
        return (arg1, arg2)

    def extractFromReference(self, line):

        ref = ""
        icdCode = ""
        content = ""
        try:
            rc = re.compile("^(?P<type>[TNRA])(?P<id>[\d]+)[\t ]*(?P<typename>[A-Za-z]+)[\t ]*(?P<ref>[TNRA][\d]+)[\t ]*(?P<icd>ICD10:)(?P<icdCode>[^ \t]+)[\t ]*(?P<content>.*)")
            for entry in [m.groupdict() for m in rc.finditer(line)]:
                ref = entry["ref"]
                icdCode = entry["icdCode"]
                content = entry["content"]
        except:
            print("reference extraction error for: " + line)
        return (ref, icdCode, content)

    def extractFromConditionTypeLine(self, line):
        pos1 = ""
        pos2 = ""
        content = ""
        try:
            rc = re.compile("^(?P<type>[TNRA])(?P<id>[\d]+)[\t ]*(?P<typename>[A-Za-z_]+)[\t ]*(?P<pos1>[\d]+)[\t ]*(?P<pos2>[\d]+)[\t ]*(?P<content>.*)")
            for entry in [m.groupdict() for m in rc.finditer(line)]:
                pos1 = entry["pos1"]
                pos2 = entry["pos2"]
                content = entry["content"]
        except:
            print("ConditionType extraction error for: " + line)
        return (pos1, pos2, content)

    def extractFromOldAnnotations(self, payload):
        payload.status = "ExtractDataFromAnnotations"
        for anot in payload.annotations:
            annotations = anot["annotations"]
            for annotation in annotations:
                for entry in annotationAdditionalMap:
                    if nodata(payload.patient.medicalData, entry):
                        recipe = annotationAdditionalMap[entry]
                        try:
                            if recipe["entryType"] == "exists":
                                payload.patient.medicalData[entry] = 0
                                if recipe["type"] == annotation["type"] and recipe["subtype"] == annotation["subtype"] and re.search(recipe["valueRegex"], annotation["value"]) != None:
                                    payload.patient.medicalData[entry] = 1
                        except:
                            # key does not exist, skipping
                            pass

            for synonym in synonymsMap:
                if nodata(payload.patient.medicalData, synonym):
                    for annotation in annotations:
                        recipe = synonymsMap[synonym]
                        try:
                            if recipe["entryType"] == "exists":
                                payload.patient.medicalData[synonym] = 0
                                if recipe["type"] == "Condition" \
                                        and re.search(recipe["valueRegex"], annotation["value"]) != None:
                                    payload.patient.medicalData[synonym] = 1
                        except:
                            # key does not exist, skipping
                            pass
