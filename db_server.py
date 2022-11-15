import json
import os
import sys
import threading
from json import JSONDecodeError

import jsonschema
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from pymongo import MongoClient

import nlp_pipeline.nlp_server
#####################################################################################
# 0) Root
#####################################################################################
from recommendation.aux.service.TraceLog import TraceLog

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

PIPELINE_ROOT = "/mnt/STORAGE/projects/mediplanner_community/"
PIPELINE_ROOT = "/home/mediplanner/dev/mediplanner_p/mediplanner/"
PIPELINE_NLP_FOLDER = PIPELINE_ROOT + "nlp_pipeline/"
PIPELINE_WORK_FOLDER = PIPELINE_ROOT + "nlp_pipeline/work/"
PIPELINE_WORK_CRF_FOLDER = PIPELINE_ROOT + "nlp_pipeline/work/crf/"
PIPELINE_WORK_RESULTS_FOLDER = PIPELINE_ROOT + "nlp_pipeline/work/results"

SERVER_IP = "127.0.0.1"
VERSION = "0.5"
HELLO_MSG = "<h1>Welcome to SapiHub MediPlanner server ver. " + VERSION + "</h1>"
DB_NAMES = ["repository", "main"]
DB_OPERATIONS = ["add_one", "get_one", "get_many", "delete_one", "delete_many", "update_one", "update_many", "count"]
COLLECTIONS = ["medicalData", "patients", "annotations", "diagnoses", "treatment_plans", "risks", "interviews", "visits", "recommendations"]

#####################################################################################

app = Flask(__name__)


#####################################################################################

class MediPlannerServer():
    mongoClient = MongoClient('mongodb://127.0.0.1:27017/')
    httpServer = None
    nlpSrv = None
    jsonSchemes = {}

    def runHttpServer(self, serverIp):

        httpServer = WSGIServer((serverIp, 8090), app)
        httpServer.serve_forever()

    def run(self, serverIp):

        if serverIp == "":
            serverIp = SERVER_IP

        # mongoClient.repository.authenticate('user', 'pass',mechanism='SCRAM-SHA-1')

        t = threading.Thread(target=self.runHttpServer, args=(serverIp,))
        t.daemon = True
        print("Starting HTTP server...")
        t.start()
        print("HTTP server started.")

        self.nlpSrv = nlp_pipeline.nlp_server.NLPServer(self.mongoClient)
        self.nlpSrv.run()

    #####################################################################################
    # 1) Input JSON validation (via schemes)
    #####################################################################################

    def loadSchema(self, tname, fname):
        print("loadSchema, tname = " + tname)
        f = open(fname, "r", encoding="utf-8")
        s = "".join(f.readlines())
        f.close()
        if s != "":
            self.jsonSchemes[tname] = json.loads(s)

    def loadSchemes(self):
        self.loadSchema("patients", "db_json_schemes/template_patient.json")
        self.loadSchema("annotations", "db_json_schemes/template_annotation.json")
        self.loadSchema("diagnoses", "db_json_schemes/template_diagnosis.json")
        self.loadSchema("treatment_plans", "db_json_schemes/template_treatment_plan.json")
        self.loadSchema("risks", "db_json_schemes/template_risk.json")

    def validateJson(self, js, schemaName):
        try:
            sch = self.jsonSchemes[schemaName]
            print(sch)
            print(js)
            r = jsonschema.validate(instance=js, schema=sch)
            print(r)
        except jsonschema.exceptions.ValidationError as err:
            return (False, str(err.message) + ':' + str(err.path))

        return (True, "OK")

    def rootResult(self):
        result = "<!DOCTYPE html><html><head><style>body { margin-top: 150px; text-align: center; color: white; " \
                 "font-family: Calibri, Arial; background-color: darkcyan;}</style></head><body> "
        result += HELLO_MSG
        result += "<a style='color: white;' href='/mediplanner/view?db=repository&collection=patients'>1) Example view of " \
                  "patients collection<br>(don't forget to run db_test.py before)</a><br><br> "
        result += "<a style='color: white;' href='/mediplanner/view?db=repository&collection=annotations'>2) Example view " \
                  "of annotations collection</a><br><br> "
        result += "<h3>Powered by Flask+MongoDB</h3>"  # (" + str(datetime.datetime.now()) + ")</h3>"
        result += "</body></html>"

        return result

    def makeResponse(self, code, body):
        d = {"returnCode": code, "body": body}

        try:
            s = json.dumps(d)
        except JSONDecodeError as e:
            s = json.dumps({"returnCode": "InternalError", "body": "Invalid JSON in make_response()"})

        return s


#####################################################################################

print("Starting MediPlanner server...")
mps = MediPlannerServer()
print("MediPlanner server started.")


#####################################################################################


@app.route("/mediplanner", methods=["GET"])
def handleRoot():
    return mps.rootResult()


@app.route("/mediplanner/", methods=["GET"])
def handleRoot2():
    return mps.rootResult()


#####################################################################################
# 2a) View operations (debug purposes)
#####################################################################################

@app.route("/mediplanner/view", methods=["GET"])
def processView():
    dbname = request.args.get('db')
    if not dbname in DB_NAMES:
        result = "Invalid database name."
        return result

    collname = request.args.get('collection')
    if not collname in COLLECTIONS:
        result = "Invalid collection name."
        return result

    db = mps.mongoClient.get_database(dbname)

    result = "<!DOCTYPE html><html><head><style>body { font-family: Calibri, Arial; color: white; background-color: " \
             "darkcyan;}</style></head><body> "
    result += "<h1 style='color: white;'>Collection [" + collname + "]</h1>"
    result += "<hr style='border: 1px solid white;'>"

    l = []
    for e in db[collname].find():
        l.append(e)

    i = 0
    for e in l:
        result += "<h3 style='color: white;'>Item #" + str(i) + ":</h3>"
        if collname == "patients":
            result += e["patientIdentifier"] + ", " + e["dateAdded"]
        elif collname == "annotations":
            result += str(e["annotations"])
        else:
            result += str(e)
        result += "</br></br><hr style='border: 1px solid white;'></hr>"
        i += 1
    result += "</body></html>"

    return mps.makeResponse("OK", result)


#####################################################################################
# 2b) Count operations (debug purposes)
#####################################################################################

@app.route("/mediplanner/count", methods=["GET"])
def processCount():
    dbname = request.args.get('db')
    if not dbname in DB_NAMES:
        result = "Invalid database name."
        return result

    collname = request.args.get('collection')
    if not collname in COLLECTIONS:
        result = "Invalid collection name."
        return result

    db = mps.mongoClient.get_database(dbname)

    n = db[collname].count_documents({})
    print('count_documents = ' + str(n))

    result = str(n) + " item(s) in " + collname + "."

    return mps.makeResponse("OK", result)


#####################################################################################
# 2c) Clear operations (debug purposes)
#####################################################################################

@app.route("/mediplanner/clear", methods=["GET"])
def processClear():
    dbname = request.args.get('db')
    if not dbname in DB_NAMES:
        result = "Invalid database name."
        return result

    collname = request.args.get('collection')
    if not collname in COLLECTIONS:
        result = "Invalid collection name."
        return result

    db = mps.mongoClient.get_database(dbname)

    r = db[collname].delete_many({})
    print('deleted_documents = ' + str(r.deleted_count))

    result = str(r.deleted_count) + " item(s) from " + collname + " deleted."

    return mps.makeResponse("OK", result)


#####################################################################################
# 2d) Test (by GET) operations (debug purposes)
#####################################################################################

# @app.route("/mediplanner/test", methods=["GET"])
# def processTest():
#
#     dbname = request.args.get('db')
#     if not dbname in DB_NAMES:
#         result = "Invalid database name."
#         return result
#
#     db = client.get_database(dbname)
#
#     result = flask_test.run_test(dbname)
#
#     return make_response("OK", result)

#####################################################################################
# 3) CRUD operations : todo: @app.route("/mediplanner/process/addPatient"... etc.
#####################################################################################

def preprocessJson(js):
    if not js == None:
        try:
            s = str(js)

            q_count = s.count("\\\"")
            if q_count > 0:
                s = s.replace("\\""", "'")

            single_cnt = s.count("'")
            double_cnt = s.count("\"")

            if single_cnt > double_cnt:
                s = s.replace("'", "\"")

            result = "OK"
            dict = json.loads(s)
        except JSONDecodeError as e:
            print('preprocessJson() error = ' + str(e))
            result = "Invalid JSON argument in processMain()"
            dict = {}

        return (result, dict)


def getDb(request):
    dbname = request.args.get('db')
    if not dbname in DB_NAMES:
        resultCode = "Error"
        result = "Invalid database name."
        return mps.makeResponse(resultCode, result)

    db = mps.mongoClient.get_database(dbname)

    return db


def createObject(request, collname):
    db = getDb(request)

    (result_js, dict) = preprocessJson(request.body)
    if result_js == "OK":
        insert_result = db[collname].insert_one(dict)
        resultCode = "OK"
        result = str(insert_result.inserted_id)
    else:
        resultCode = "Error"
        result = "Invalid JSON structure: " + request.body

    return mps.makeResponse(resultCode, result)


def getObject(request, collname):
    db = getDb(request)

    (result_js, dict) = preprocessJson(request.body)

    result = db[collname].find_one(dict)
    resultCode = "OK"

    return mps.makeResponse(resultCode, result)


def updateObject(request, collname):
    db = getDb(request)

    (result_js, dict) = preprocessJson(request.body)

    d_filter = dict["filter"]
    d_update = dict["update"]

    result = db[collname].update_one(d_filter, d_update)
    resultCode = "OK"

    return mps.makeResponse(resultCode, result)


def deleteObject(request, collname):
    db = getDb(request)

    (result_js, dict) = preprocessJson(request.body)

    result = db[collname].delete_one(dict)
    resultCode = "OK"

    return mps.makeResponse(resultCode, result)


#####################################################################################

@app.route("/mediplanner/db/patients/createPatient", methods=["POST"])
def processMainAddPatient():
    result = createObject(request, "patients")

    return result


@app.route("/mediplanner/db/patients/getPatient", methods=["POST"])
def processMainGetPatient():
    result = getObject(request, "patients")

    return result


@app.route("/mediplanner/db/patients/updatePatient", methods=["POST"])
def processMainUpdatePatient():
    result = updateObject(request, "patients")

    return result


@app.route("/mediplanner/db/patients/deletePatient", methods=["POST"])
def processMainDeletePatient():
    result = deleteObject(request, "patients")

    return result


#####################################################################################

@app.route("/mediplanner/db/patients/createInterview", methods=["POST"])
def processMainAddInterview():
    result = createObject(request, "interviews")

    return result


@app.route("/mediplanner/db/patients/getInterview", methods=["POST"])
def processMainGetInterview():
    result = getObject(request, "interviews")

    return result


@app.route("/mediplanner/db/patients/updateInterview", methods=["POST"])
def processMainUpdateInterview():
    result = updateObject(request, "interviews")

    return result


@app.route("/mediplanner/db/patients/deleteInterview", methods=["POST"])
def processMainDeleteInterview():
    result = deleteObject(request, "interviews")

    return result


#####################################################################################

@app.route("/mediplanner/db/annotations/createAnnotation", methods=["POST"])
def processMainAddAnnotation():
    result = createObject(request, "annotations")

    return result


@app.route("/mediplanner/db/annotations/getAnnotation", methods=["POST"])
def processMainGetAnnotation():
    result = getObject(request, "annotations")

    return result


@app.route("/mediplanner/db/annotations/updateAnnotation", methods=["POST"])
def processMainUpdateAnnotation():
    result = updateObject(request, "annotations")

    return result


@app.route("/mediplanner/db/annotations/deleteAnnotation", methods=["POST"])
def processMainDeleteAnnotation():
    result = deleteObject(request, "annotations")

    return result


#####################################################################################

@app.route("/mediplanner/db/diagnoses/createDiagnosis", methods=["POST"])
def processMainAddDiagnosis():
    result = createObject(request, "diagnoses")

    return result


@app.route("/mediplanner/db/diagnoses/getDiagnosis", methods=["POST"])
def processMainGetDiagnosis():
    result = getObject(request, "diagnoses")

    return result


@app.route("/mediplanner/db/diagnoses/updateDiagnosis", methods=["POST"])
def processMainUpdateDiagnosis():
    result = updateObject(request, "diagnoses")

    return result


@app.route("/mediplanner/db/diagnoses/deleteDiagnosis", methods=["POST"])
def processMainDeleteDiagnosis():
    result = deleteObject(request, "diagnoses")

    return result


#####################################################################################

@app.route("/mediplanner/db/risks/createRisk", methods=["POST"])
def processMainAddRisk():
    result = createObject(request, "risks")

    return result


@app.route("/mediplanner/db/risks/getRisk", methods=["POST"])
def processMainGetRisk():
    result = getObject(request, "risks")

    return result


@app.route("/mediplanner/db/risks/updateRisk", methods=["POST"])
def processMainUpdateRisk():
    result = updateObject(request, "risks")

    return result


@app.route("/mediplanner/db/risks/deleteRisk", methods=["POST"])
def processMainDeleteRisk():
    result = deleteObject(request, "risks")

    return result


#####################################################################################

@app.route("/mediplanner/db/treatmentPlans/createTreatmentPlan", methods=["POST"])
def processMainAddTreatmentPlan():
    result = createObject(request, "treatment_plans")

    return result


@app.route("/mediplanner/db/treatmentPlans/getTreatmentPlan", methods=["POST"])
def processMainGetTreatmentPlan():
    result = getObject(request, "treatment_plans")

    return result


@app.route("/mediplanner/db/treatmentPlans/updateTreatmentPlan", methods=["POST"])
def processMainUpdateTreatmentPlan():
    result = updateObject(request, "treatment_plans")

    return result


@app.route("/mediplanner/db/treatmentPlans/deleteTreatmentPlan", methods=["POST"])
def processMainDeleteTreatmentPlan():
    result = deleteObject(request, "treatment_plans")

    return result


#####################################################################################
# 3b) NLP server operations :
#####################################################################################


@app.route("/mediplanner/nlp/request/<externalSessionId>", methods=["POST"])
def processNlpRequestP(externalSessionId):
    TraceLog().add(externalSessionId, "Nlp processing started ...")
    return processNlp(request.data.decode("utf-8"), externalSessionId)


@app.route("/mediplanner/nlp/request", methods=["POST"])
def processNlpRequest():
    return processNlp(request.data.decode("utf-8"), None)


def processNlp(req, externalSessionId):
    guid = mps.nlpSrv.getRequestGuid()
    mps.nlpSrv.thrProcessor.putSysMsg(nlp_pipeline.nlp_server.NLPServerMessage(None, "INCOMING_OP", "LOCAL_REQUEST", req, guid))
    return mps.makeResponse("OK", guid)


@app.route("/mediplanner/nlp/status/<externalSessionId>", methods=["POST"])
def processNlpStatusP(externalSessionId):
    guid = request.data.decode("utf-8")

    status = getStatus(guid)
    TraceLog().add(externalSessionId, "Nlp status checked ..." + status)
    return status


@app.route("/mediplanner/nlp/status", methods=["POST"])
def processNlpStatus():
    guid = request.data.decode("utf-8")

    return getStatus(guid)


def getStatus(guid):
    # Check if result file exists - no need to check current pipeline status
    baseDir = os.getcwd()
    os.chdir(PIPELINE_WORK_RESULTS_FOLDER)
    resultCode = "OK"
    # sPath = "work/results/" + guid + "/tmp_input.json"
    if os.path.isdir(guid):
        status = "OK"
    else:
        if not os.path.isdir(guid + "_out"):
            os.mkdir(guid + "_out")
        else:
            try:
                os.mkdir(guid + "_out_fallback")
            except:
                pass
        status = "OK" if os.path.isdir(guid + "_out_fallback") else "PENDING"
    os.chdir(baseDir)
    return mps.makeResponse(resultCode, status)


@app.route("/mediplanner/nlp/result/<externalSessionId>", methods=["POST"])
def processNlpResultP(externalSessionId):
    guid = request.data.decode("utf-8")

    result = getResult(guid)
    TraceLog().add(externalSessionId, "Nlp result sent to Mediator ...")
    return result


@app.route("/mediplanner/nlp/result", methods=["POST"])
def processNlpResult():
    guid = request.data.decode("utf-8")

    return getResult(guid)


def getResult(guid):
    baseDir = os.getcwd()
    # fix for the recurrent directory error:
    os.chdir(PIPELINE_WORK_RESULTS_FOLDER)
    TraceLog().add(guid, "read response ")
    s = ""
    try:
        f = open(guid + "/tmp_input.json", "r", encoding="utf-8")
        s = f.read()
        f.close()
        TraceLog().add(guid, " response ready")
    except:
        f = open(PIPELINE_WORK_RESULTS_FOLDER +"/"+guid + "_fallback.json", "r", encoding="utf-8")
        s = f.read()
        f.close()
        TraceLog().add(guid, " response constructed")
    if not s == "":
        resultCode = "OK"
    else:
        resultCode = "Error"
    os.chdir(baseDir)

    response = mps.makeResponse(resultCode, s)
    TraceLog().add(guid, "preparing response ")
    return response


#####################################################################################
# 4) Wrapper operations :
#####################################################################################


@app.route("/mediplanner/process", methods=["GET", "POST"])
def processMain():
    resultCode = "OK"

    method = request.method
    print('Method is ' + str(method))

    dbname = request.args.get('db')
    if not dbname in DB_NAMES:
        resultCode = "Error"
        result = "Invalid database name."
        return mps.makeResponse(resultCode, result)

    collname = request.args.get('collection')
    if not collname in COLLECTIONS:
        resultCode = "Error"
        result = "Invalid collection name."
        return mps.makeResponse(resultCode, result)

    arg = request.args.get('op')
    if not arg in DB_OPERATIONS:
        resultCode = "Error"
        result = "Invalid DB operation."
        return mps.makeResponse(resultCode, result)

    db = mps.mongoClient.get_database(dbname)

    print("processMain() request.json = " + str(request.json))

    (result, dict) = preprocessJson(request.json)

    if result != "OK":
        print("JSON error in preprocessJson()")
        return mps.makeResponse("Error", "JSON error")

    print("processMain() dict = " + str(dict))

    result = ""
    if method == "POST":
        if arg == "add_one":

            validationResult = True
            if "validate" in request.args:
                validate = request.args.get('validate')
                if validate == "yes":
                    (validationResult, msg) = mps.validateJson(dict, collname)

            if validationResult:
                insert_result = db[collname].insert_one(dict)
                result = str(insert_result.inserted_id)
            else:
                resultCode = "Error"
                result = "Invalid JSON structure in validation: " + msg

        elif arg == "delete_one":

            delete_result = db[collname].delete_one(dict)

            result = str(delete_result.deleted_count)

        elif arg == "delete_many":

            delete_result = db[collname].delete_many(dict)

            result = str(delete_result.deleted_count)

        elif arg == "update_one":

            dict_filter = dict["filter"]
            dict_update = {'$set': dict["update"]}

            update_result = db[collname].update_one(dict_filter, dict_update)

            result = str(update_result)

        elif arg == "update_many":

            dict_filter = dict["filter"]
            dict_update = dict["update"]

            update_result = db[collname].update_many(dict_filter, dict_update)

            result = str(update_result)

        elif arg == "count":

            n = db[collname].count_documents({})

            result = str(n)

        elif arg == "get_one":

            find_result = db[collname].find_one(dict)

            result = str(find_result)

        elif arg == "get_many":

            find_cursor = db[collname].find(dict)

            l = list(find_cursor)

            result = str(l)
        else:
            result = "Invalid DB operation for POST"

    return mps.makeResponse(resultCode, result)


#####################################################################################


if __name__ == "__main__":

    print("Initial dir = " + os.getcwd())

    mps.loadSchemes()

    cnt = len(sys.argv)
    if cnt == 1:
        mps.run("")
    elif cnt == 2:
        mps.run(sys.argv[1])
