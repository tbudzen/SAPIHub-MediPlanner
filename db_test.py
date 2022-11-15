from flask import Flask, request

import json
import requests

HOST = "127.0.0.1"

def loadJsonFile(fname):

    f = open(fname, "r", encoding="utf-8")
    s = "".join(f.readlines())
    f.close()
    j = json.loads(s)

    return j

def testTemplates(db):

    js = []
    js.append(("annotations", loadJsonFile("db_json_tests/json_test_annotation.json")))
    js.append(("diagnoses", loadJsonFile("db_json_tests/json_test_diagnosis.json")))
    js.append(("patients", loadJsonFile("db_json_tests/json_test_patient.json")))
    js.append(("risks", loadJsonFile("db_json_tests/json_test_risk.json")))
    js.append(("treatment_plans", loadJsonFile("db_json_tests/json_test_treatment_plan.json")))

    for (coll, el) in js:
        r = requests.post("http://localhost:8090/mediplanner/process?db=" +
                          db + "&collection=" + coll + "&op=add_one", data=json.dumps(el))
        print(r.text)


def run_test(dbname):
    requestText = \
        "{ \
       \"patientIdentifier\":\"Jan Kowalski\",\
       \"dateAdded\":\"2020-nnkjnknj09-06\",\
       \"interviews\":[\
       {\
           \"date\":\"2020-09-06\",\
           \"text\":\"To jest tekst 1.\",\
           \"text_id\":\"T1\",\
           \"type\":\"podmiotowy\"\
        },\
       {\
           \"date\":\"2020-09-06\",\
           \"text\":\"To jest tekst 2.\",\
           \"text_id\":\"T2\",\
           \"type\":\"przedmiotowy\"\
        }\
        ],\
        \"medicalData\":[{\
         \"date\":\"2020-09-06\",\
         \"identifier\":\"B1\",\
         \"err\":\"B1\",\
         \"type\":\"<String>\",\
         \"value\":\"<String>\",\
         \"unit\":\"<String>\",\
         \"stringRepresentation\":\"<String>\"\
        }]}"

    s2 = \
        "{ \
       \"patientIdentifier\":\"Anna Kowalska\",\
        \"testCount\":0,\
       \"dateAdded\":\"2020-09-06\",\
       \"interviews\":[\
       {\
           \"date\":\"2020aaaaa-09-06\",\
           \"text\":\"To jest tekst 1.\",\
           \"text_id\":\"T1\",\
           \"type\":\"podmiotowy\"\
        },\
       {\
           \"date\":\"2020-09-06\",\
           \"text\":\"To jest tekst 2.\",\
           \"text_id\":\"T2\",\
           \"type\":\"przedmiotowy\"\
        }\
        ],\
        \"medicalData\":[{\
         \"date\":\"2020-09-06\",\
         \"identifier\":\"B1\",\
         \"type\":\"<String>\",\
         \"value\":\"<String>\",\
         \"unit\":\"<String>\",\
         \"stringRepresentation\":\"<String>\"\
        }]}"

    result = ""

    for i in range(10):
        r = requests.post('http://' + HOST + ':8080/mediplanner/process?db=' + dbname + '&collection=patients&op=add_one', data=requestText)
        print(r.text)
        result += r.text
        r = requests.post('http://' + HOST + ':8080/mediplanner/process?db=' + dbname + '&collection=patients&op=add_one', data=s2)
        print(r.text)
        result += r.text

    r = requests.post('http://' + HOST + ':8080/mediplanner/process?db=' + dbname + '&collection=patients&op=count')
    print(r.text)
    result += r.text

    sget = "{ \"a\" : \"1\" }"
    r = requests.post('http://' + HOST + ':8080/mediplanner/process?db=' + dbname + '&collection=patients&op=get_one', data=sget)
    print(r.text)
    result += r.text
    r = requests.post('http://' + HOST + ':8080/mediplanner/process?db=' + dbname + '&collection=patients&op=get_many', data=sget)
    print(r.text)
    result += r.text

    sget = "{ \"interviews.type\":\"podmiotowy\", \"patientIdentifier\":\"Anna Kowalska\" }"
    r = requests.post('http://' + HOST + ':8080/mediplanner/process?db=' + dbname + '&collection=patients&op=get_many', data=sget)
    print(r.text)
    result += r.text

    #sget = "{ \"patientIdentifier\" : \"Anna Kowalska\" }"
    #r = requests.post('http://localhost:8080/mediplanner/process?db=' + dbname + '&collection=patients&op=delete_many', json=sget)
    #print(r.text)
    #result += r.text

    supdate = "{ \"filter\" : { \"patientIdentifier\" : \"Anna Kowalska\" }, \"update\" : { \"$inc\": { \"testCount\": 7 } } }"
    r = requests.post('http://' + HOST + ':8080/mediplanner/process?db=' + dbname + '&collection=patients&op=update_many', data=supdate)
    print(r.text)
    result += r.text

    return result

def run_test_error_1():

    sget = "abc"
    r = requests.post('http://' + HOST + ':8080/mediplanner/process?db=repository&collection=patients&op=get_one', data=sget)
    print(r.text)

#run_test_error_1()
run_test("repository")

#testTemplates("repository")
