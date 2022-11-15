#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pprint import pprint
import numpy as np
import sys
import json
from pygments import highlight, lexers, formatters
from datetime import datetime
import pandas as pd
import sqlite3
from sqlite3 import Error
from typing import List
from typing import Set
import functools
from functools import reduce

dateFormat = "%Y-%m-%d %H:%M:%S.%f"
databaseFile = r"meds_all_data.db"
patientsFile = "mediplanner_2016_AN.xls"


def writeToFile(lines, filename):
    outF = open(filename, "w")
    outF.writelines(lines)
    outF.close()

def executeSelect(sqlScript):
    conn = sqlite3.connect('meds_all_data.db')
    c = conn.cursor()
    c.execute(sqlScript)
    result = c.fetchall()
    conn.close()
    return result


def asCsvLine(emements: List):
    return "\t".join(emements) + "\n"

def asCommaSeparated(elements: List):
    return ",".join(elements)

class Mapping:
    def __init__(self, original, tradename = "", substance = "", atc = ""):
        self.original = original
        self.tradename = tradename
        self.substance = substance
        self.atc = atc
    def __str__(self):
        return f"[[{self.mappingCode()}]:{self.original}->{self.substance}->{self.atc}]"
    def mappingCode(self):
        if self.tradename == "":
            return "S"
        else:
            return "T"
    def update(self, substance, atc):
        if substance == self.substance:
            self.atc = atc

class ATC:
    def __init__(self, code):
        self.code = code
        sqlScript = f"select * from atc where code like '{code}'"
        resultList = executeSelect(sqlScript)
        if len(resultList) > 0:
            self.name = resultList[0][2]
            self.nameEn = resultList[0][3]
        else:
            self.name = "unknown"
            self.nameEn = "unknown"
            
    def __str__(self):
        return f"[{self.code}: {self.name}]"
            
        

class MedicinesForHospitalStay:
    def __init__(self, hospitalStay, patientId, medicinesDescription = "nan"):
        self.hospitalStay = hospitalStay
        self.patientId = patientId
        self.medicinesDescription = str(medicinesDescription).replace("\t", " ")
        self.mixedNames = []
        self.substances = []
        self.tradenames = []
        self.substancesFromTradeNames = []
        self.notRecognized = []
        self.allSubstances = []
        self.atcs = []
        self.mappings = []
        
    
    def __str__(self):
        return f"MedicinesforHospitalStay[{self.hospitalStay}, {self.medicinesDescription},\n {self.substances} \n{self.mixedNames}]"
    
    def basicAttributes(self):
        pid = str(self.patientId)
        hs = str(self.hospitalStay)
        md = str(self.medicinesDescription)
        sbs = ','.join(self.allSubstances)
        nr = ','.join(self.notRecognized)
        atcs = ','.join(self.sortedAtcsCodes())
        mps = ','.join(self.mappingsStr())
        return [pid,hs,md,sbs,atcs,mps,nr]
    
    def sortedAtcsCodes(self):
        atcCodes = list(set(map(lambda atc: atc.code, self.atcs)))
        atcCodes.sort()
        return atcCodes
    
    def isSubstancePresent(self, substance):
        if substance in self.allSubstances:
            return "1"
        else:
            return "0"
    
    def csvLineCells(self, substances):
#        mappedSubstances = list(map(lambda substance: self.isSubstancePresent(substance), substances))
        return self.basicAttributes() # + mappedSubstances
    
    def csvLine(self, substances):
        return asCsvLine(self.csvLineCells(substances))
    
    def updateSubstances(self):
#        isStr = isinstance(self.medicinesDescription, str)
#        if isStr:
        splitted = self.medicinesDescription.split(",")
        splitted = list(map(lambda x: x.strip().replace('.',''), splitted))
        self.mixedNames = splitted
        self.updateForSplited(splitted)
        self.allSubstances = list(set(self.substances + self.substancesFromTradeNames))
        self.allSubstances.sort()
        print(f"substances updated: {self}")
        self.updateATCs()
        
    def updateATCs(self):
        # Żeby można było wyciągnąć skąd wzięły się grupy leków (ATC), to trzeba wykonywać zapytanie dla każdej substancji oddzielnie. Komentuję pojedyńcze zapytanie dla wszystkich substancji
        for substance in self.allSubstances:
            sqlScript = f"select distinct atc_idx from items_atc where item_idx in (select _id from items where subst_idx in (select _id from substs where name_in in ('{substance}')))"
            atcsCodes = executeSelect(sqlScript)
            for actCode in atcsCodes:
                atc = ATC(actCode[0])
                self.atcs.append(atc)
                self.updateMappings(substance, atc.code)
#        substancesList = "'" + "','".join(self.allSubstances) + "'"
#        sqlScript = f"select distinct atc_idx from items_atc where item_idx in (select _id from items where subst_idx in (select _id from substs where name_in in ({substancesList})))"
#        atcsCodes = executeSelect(sqlScript)
#        for actCode in atcsCodes:
#            self.atcs.append(ATC(actCode[0]))
    def updateMappings(self, substance, atcCode):
        for mapping in self.mappings:
            mapping.update(substance, atcCode)
    
    def updateForSplited(self, splitted):
        for suspect in splitted:
            suspectSubstances = self.findSuspectSubstances(suspect)
            if self.isSubstance(suspectSubstances):
                inName = suspectSubstances[0][0]
                self.substances.append(inName)
                self.mappings.append(Mapping(original = suspect, tradename = "", substance = inName, atc = ""))
            else:
                if self.isTradeName(suspect):
                    self.tradenames.append(suspect)
                    substances = self.findSubstance(suspect)
                    if len(substances) > 0:
                        subst = substances[0][0]
                        if isinstance(subst, str):
                            self.substancesFromTradeNames.append(subst)
                            self.mappings.append(Mapping(original = suspect, tradename = suspect, substance = subst, atc = ""))
                else:
                    self.notRecognized.append(suspect)
    
    def findSubstance(self, tradename):
        sqlScript = f"select name_in from substs where _id in (select subst_idx from items where tradename_idx in (select _id from tradenames where name like '{tradename}'))"
        return executeSelect(sqlScript)
    def findSuspectSubstances(self, suspect):
        sqlScript = f"select name_in from substs where name_in like '{suspect}' or name_pl like '{suspect}' or name_la like '{suspect}'"
        return executeSelect(sqlScript)
    def isSubstance(self, suspectSubstances):
        return len(suspectSubstances) > 0
    def isTradeName(self, suspect):
        sqlScript = f"select * from tradenames where name like '{suspect}'"
        resultList = executeSelect(sqlScript)
        isFound = len(resultList) > 0
        return isFound
    def mappingsStr(self):
        return list(map(lambda x: str(x), self.mappings))
    

def columnTitlesForSubstances(substancesList: List):
    return ["patientId", "hospitalStay", "medicinesDescription", "substances", "ATCs", "mappings", "notRecognized"]
   

def addSubstanceToSet(substanceSet: Set, mfhs: MedicinesForHospitalStay):
    substanceSet.allSubstances

def writeMedicinesForHospitalStaysToFile(medicinesForHospitalStays: List):
    print("writeMedicinesForHospitalStaysToFile")
    print(f"hospital stays: {len(medicinesForHospitalStays)}")
    substancesSet = reduce(lambda s,mfhs: s.union(mfhs.allSubstances), medicinesForHospitalStays, set())
    substancesList = list(substancesSet)
    substancesList.sort()
    print(f"{substancesList}")
    linesForFile = [asCsvLine(columnTitlesForSubstances(substancesList))]
    linesForFile += list(map(lambda mfhs: mfhs.csvLine(substancesList), medicinesForHospitalStays))
    writeToFile(linesForFile, "substances6.csv")
    


class SubjectStudy:
    key: str
    value: str
    unit: str
    full: str
    type: str
    created: str
    def __init__(self):
        self.key = None
        self.value = None
        self.unit = None
        self.full = None
        self.type = None
        self.created = None
    def __str__(self):
        return self.key + " " + self.value + " " + self.unit + " " + self.full + " " + self.type 

class HospitalStay:
    def __init__(self):
        self.icd9 = []
        self.icd10 = []
        self.subjectStudies = {}
        self.descriptiveMedicalDatas = {}
        self.diagnosticTests = []
        self.generalUrineTest = {}
        self.elementsOfNonCentrifugedUrine = {}
        self.morphology = {}
    id: int
    unit: str
    doctorId: int
    startDate: str
    endDate: str
    icd9: []
    icd10: []
    created: str
    doctorDiagnosises: str
    subjectStudies: {}
    descriptiveMedicalDatas: {}
    diagnosticTests: []
    generalUrineTest: {}
    elementsOfNonCentrifugedUrine: {}
    morphology: {}
        
class Patient:
    def __init__(self):
        self.hospitalStay = {}
    id: int
    hospitalStay: {}
    age: int
    sex: str
    def __str__(self):
        return self.id + " " + self.age + " " + self.sex
    
class DescriptiveMedicalData:
    key: str
    value: str
    def __str__(self):
        return self.key + " " + self.value
        
class DiagnosticTests:
    key: str
    value: str
    def __str__(self):
        return self.key + " " + self.value
    
def is_not_blank(s):
    return bool(s and s.strip())

def parseDateTime(inputDateTime):
    return datetime.strptime(inputDateTime, dateFormat)
    
def removeDelimiters(inputString):

    if not isinstance(inputString, str): 
        return inputString;
    
    if inputString.startswith('>\''):
        inputString = inputString[2:]
    elif inputString.startswith('>'):
        inputString = inputString[1:]

    if inputString.endswith('\'<'):
        inputString = inputString[:-2]      
    elif inputString.endswith('<'):
        inputString = inputString[:-1] 
    
    if inputString.startswith("'"):
        inputString = inputString[1:]
    if inputString.endswith("'"):
        inputString = inputString[:-1]
    
    return inputString

def toJson(obj):
    formatted_json= json.dumps(obj, default = lambda x: x.__dict__, sort_keys=True,indent=4,ensure_ascii=False)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    return formatted_json.replace('\\\\x0d\\\\x0a', '\n')

def readPatientsFromFile(path: str, existingPatients: dict):
    recordsFromFile = parseXlsFile(path)
    addNewPatients(recordsFromFile, existingPatients)
    return buildPatientsArray(existingPatients)
        
def parseXlsFile(path) -> pd.DataFrame:
    patientsDf = pd.read_excel(path, sheet_name='Arkusz1', header=None)
    for i in range(0, patientsDf.shape[1] - 1):
        patientsDf[i] = patientsDf[i].apply(removeDelimiters)
    return patientsDf

def addNewPatients(recordsFromFile: pd.DataFrame, existingPatients: dict):
    for index, row in recordsFromFile.iterrows():
        buildPatient(existingPatients, row)

def buildPatient(patients, tab) -> Patient:
    
    if tab[0] in patients:
        patient = patients[tab[0]]
    else:
        patient = Patient()
        patient.id = tab[0]
        patient.age = tab[7]
        patient.sex = tab[8]
        patients[tab[0]] = patient
    
    if tab[1] not in patient.hospitalStay:
        hospitalStay = HospitalStay()
        hospitalStay.id = tab[1]
        hospitalStay.unit = tab[2]
        hospitalStay.doctorId = tab[3]
        hospitalStay.startDate = tab[5]
        hospitalStay.endDate = tab[6]
        hospitalStay.icd9 = tab[9].split("<|>")
        hospitalStay.icd10 = tab[10].split("<|>")
#        hospitalStay.subjectStudy.append(subjectStudy)
        patient.hospitalStay[tab[1]] = hospitalStay;

    if tab[4] == 'Badania diagnostyczne':
        diagnosticTests = DiagnosticTests()
        diagnosticTests.key = tab[12]
        diagnosticTests.value = tab[13]
        patient.hospitalStay[tab[1]].diagnosticTests.append(diagnosticTests);
    elif tab[4] == 'Wyniki badań lab':
        if not pd.isnull(tab[13]) and is_not_blank(tab[13]) and not tab[13].startswith('COMMENT_HL7'):    
            if tab[12] == 'Badanie ogólne moczu':
                if not patient.hospitalStay[tab[1]].generalUrineTest or parseDateTime(tab[11]) > parseDateTime(patient.hospitalStay[tab[1]].generalUrineTest['created']):                   
                    patient.hospitalStay[tab[1]].generalUrineTest['created'] = tab[11]
                    patient.hospitalStay[tab[1]].generalUrineTest['value'] = tab[13]
                    urineTests = parseStringTestsResult(tab[13], 'omocz_')
                    for urineKey, urineValue in urineTests.items():
                        subjectStudy = SubjectStudy()
                        subjectStudy.key = urineKey
                        subjectStudy.type = tab[4]
                        subjectStudy.created = tab[11]
                        subjectStudy.value = urineValue
                        subjectStudy.unit = ''
                        patient.hospitalStay[tab[1]].subjectStudies[subjectStudy.key] = subjectStudy
                        
            elif tab[12] == 'Badanie - Elementy  moczu niewirowanego':
                if not patient.hospitalStay[tab[1]].elementsOfNonCentrifugedUrine or parseDateTime(tab[11]) > parseDateTime(patient.hospitalStay[tab[1]].elementsOfNonCentrifugedUrine['created']):                   
                    patient.hospitalStay[tab[1]].elementsOfNonCentrifugedUrine['created'] = tab[11]
                    patient.hospitalStay[tab[1]].elementsOfNonCentrifugedUrine['value'] = tab[13]
                    urineTests = parseStringTestsResult(tab[13], 'nmocz_')
                    for urineKey, urineValue in urineTests.items():
                        subjectStudy = SubjectStudy()
                        subjectStudy.key = urineKey
                        subjectStudy.type = tab[4]
                        subjectStudy.created = tab[11]
                        subjectStudy.value = urineValue
                        subjectStudy.unit = ''
                        patient.hospitalStay[tab[1]].subjectStudies[subjectStudy.key] = subjectStudy
            elif tab[12] == 'Morfologia':
                if not patient.hospitalStay[tab[1]].morphology or parseDateTime(tab[11]) > parseDateTime(patient.hospitalStay[tab[1]].morphology['created']):                   
                    patient.hospitalStay[tab[1]].morphology['created'] = tab[11]
                    patient.hospitalStay[tab[1]].morphology['value'] = tab[13]
                    morfTests = parseStringTestsResult(tab[13], 'mor_')
                    for morKey, morValue in morfTests.items():
                        subjectStudy = SubjectStudy()
                        subjectStudy.key = morKey
                        subjectStudy.type = tab[4]
                        subjectStudy.created = tab[11]
                        subjectStudy.full = morValue
                        splitedValue = morValue.split("[")
                        if len(splitedValue) > 1:
                            subjectStudy.value = splitedValue[0]
                        else:
                            subjectStudy.value = morValue
                            
                        if morValue.find("[") > 0 and morValue.find("]") > 0:
                            subjectStudy.unit = morValue[morValue.find("[")+1:morValue.find("]")]
                        else:
                            subjectStudy.unit = ''
                        patient.hospitalStay[tab[1]].subjectStudies[subjectStudy.key] = subjectStudy
            else:
                subjectStudy = SubjectStudy()
                subjectStudy.key = tab[12]
                subjectStudy.type = tab[4]
                subjectStudy.created = tab[11] 
                if not pd.isnull(tab[13]) and is_not_blank(tab[13]):
                    subjectStudy.value = tab[13].split(":")[1].split("[")[0]
                    subjectStudy.unit = tab[13][tab[13].find("[")+1:tab[13].find("]")]
                    subjectStudy.full = tab[13]
                if subjectStudy.key not in patient.hospitalStay[tab[1]].subjectStudies:
                    patient.hospitalStay[tab[1]].subjectStudies[subjectStudy.key] = subjectStudy
                elif parseDateTime(subjectStudy.created) > parseDateTime(patient.hospitalStay[tab[1]].subjectStudies[subjectStudy.key].created):
                    patient.hospitalStay[tab[1]].subjectStudies[subjectStudy.key] = subjectStudy
            
            #if 
            
    elif tab[4] == 'Dana medyczna opisowa':
        descriptiveMedicalData = DescriptiveMedicalData()
        descriptiveMedicalData.key = tab[12]
        descriptiveMedicalData.value = tab[13]
        patient.hospitalStay[tab[1]].descriptiveMedicalDatas[tab[12]] = tab[13];

def buildPatientsArray(patients: dict):
    patientsList = []
    for id, patient in patients.items():
        output = builPatientSeries(patient)
        for item in output:
            patientsList.append(pd.Series(item))
        #patientsDf = patientsDf.append(builPatientSeries(patient), ignore_index=True)
    return patientsList

#TO DO - nadpisane wartosci powinno zwracac tablice seri
def builPatientSeries(patient: Patient):
    output = []
    for id, hospitalStay in patient.hospitalStay.items():
        patientArray = {'id':patient.id, 'age':patient.age, 'sex':patient.sex, 'hospitalStayId':hospitalStay.id, 'hospitalStayStartDate': hospitalStay.startDate,'hospitalStayEndDate': hospitalStay.endDate}
        for subjectStudyName in hospitalStay.subjectStudies:
            patientArray[subjectStudyName] = hospitalStay.subjectStudies[subjectStudyName].value
        for diagnosticTest in hospitalStay.diagnosticTests:
            patientArray[diagnosticTest.key] = diagnosticTest.value
        for descriptiveMedicalDataKey in hospitalStay.descriptiveMedicalDatas:
            if descriptiveMedicalDataKey in hospitalStay.descriptiveMedicalDatas:
                patientArray[descriptiveMedicalDataKey] = hospitalStay.descriptiveMedicalDatas[descriptiveMedicalDataKey]
            else:
                patientArray[descriptiveMedicalDataKey] = ''
        for icd9 in hospitalStay.icd9:
            patientArray[icd9] = 1
        for icd10 in hospitalStay.icd10:
            patientArray[icd10] = 1
        output.append(patientArray)
    
    return output

def computeMedicineGroup(medicines, conn):
    output = {}
    medicinesSplited = medicines.split(",")
    for item in medicinesSplited:
        item = item.strip()
        rows = findByName(conn, item)
        if len(rows) > 0:
            output[item] = rows[0][3]
        else:
            output[item] = ''
    return output
        
#>'Barwa:jasnożółta<|>Przej:zupełna<|>SG:1.005<|>pH:8.0<|>LEU:nieobecne[ul]<|>NIT:nieobecne[ul]<|>mKET:nieobecne[mg/dl]<|>mURO:niewzmożony<|>BIL:nieobecna<|>ERY:nieobecne[ul]<|>GLU-mocz:nieobecna[mg/dl]<|>UPROT:nieobecne[mg/dl]'
def parseStringTestsResult(testResult: str, prefix: str):
    output = {}
    outputKey = []
    testResultSplited = testResult.split("<|>")
    
    for item in testResultSplited:
        splitedItem = item.split(":")
        if len(splitedItem) > 1:
            output[prefix + splitedItem[0]] = splitedItem[1]
        else:
            output[prefix + splitedItem[0]] = splitedItem[0]
        #outputKey.append(splitedItem[0])
    return output

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn

def findByName(conn, name):
    cur = conn.cursor()
    
    cur.execute("select * from doktop_descs where desc_id = (select desc_id from doktop_descs where name like ? limit 1) and col_idx = 12", (name,))
     
        
    rows = cur.fetchall()
    return rows;
#    for row in rows:
#        print(row)






existingPatientsNew = {}
patientsArray = readPatientsFromFile(patientsFile, existingPatientsNew)


hospitalStays = []

for patient in patientsArray:
    print("---------------------------------------------------------------------")
    print(patient)
df = pd.DataFrame()
df = df.append(patientsArray, ignore_index=True)
        


medicinesForHospitalStays = []
#testLines = []
for i in range(0, len(df) - 1):
    line = f"{df.at[i, 'hospitalStayId']}\t {df.at[i, 'hospitalStayId']}\t {df.at[i, 'Zastosowane leczenie']} \n"
#    testLines.append(line)
    medicinesForHospitalStays.append(MedicinesForHospitalStay(df.at[i, 'hospitalStayId'], df.at[i, 'id'], df.at[i, 'Zastosowane leczenie']))
    
#writeToFile(testLines, 'testLines.csv')
    
for medicineForHospitalStay in medicinesForHospitalStays:
    medicineForHospitalStay.updateSubstances()

writeMedicinesForHospitalStaysToFile(medicinesForHospitalStays)
