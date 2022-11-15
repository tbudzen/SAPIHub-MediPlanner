import json
import logging
import os
import re
import threading
import time

from flask import Flask, request, Response
from gevent.pywsgi import WSGIServer

from recommendation.aux.service.TraceLog import TraceLog
from recommendation.dataExtractors.dataDefinitions import dataDefinitionEntries
from recommendation.model.patient import Patient
from recommendation.payload.patient_data import Payload
from recommendation.processService.RecommendationService import RecommendationService

recomendationService = RecommendationService()

logging.basicConfig(level=logging.INFO)

VERSION = "0.4"

#####################################################################################

app = Flask(__name__)


#####################################################################################

class RecommendationServer():
    jsonSchemes = {}

    def runHttpServer(self, serverIp):
        httpServer = WSGIServer((serverIp, 9090), app)
        httpServer.serve_forever()

    def run(self):
        os.environ['FLASK_RUN_PORT'] = "9090"
        t = threading.Thread(target=self.runHttpServer, args=("0.0.0.0",))
        t.daemon = True
        print("Starting HTTP server...")
        t.start()
        print("HTTP server started.")
        while (True):
            time.sleep(0.001)


@app.route("/recommendation/process", methods=["POST"])
def processPatientData():
    requestBody = request.data.decode("utf-8")
    timestampStr = time.strftime("%Y%m%d-%H%M%S")
    saveJson(requestBody, timestampStr + "_request_")
    patient = Patient(requestBody)
    TraceLog().add(patient.patientIdentifier, "Recommendation started...")
    recommendationAndTreat = recomendationService.generate_recommendation(patient)
    response = json.dumps(recommendationAndTreat, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    saveJson(response, timestampStr + "_response_")
    TraceLog().add(patient.patientIdentifier, "<b>Recommendation processing finished succesfully, sending data to Mediator...</b><hr><br>")
    return Response(response, mimetype='application/json')


@app.route("/recommendation/processtxt", methods=["POST"])
def processPatientDataTxt():
    requestBody = request.data.decode("utf-8")
    patient = Patient(requestBody)
    recommendationAndTreat = recomendationService.generate_recommendation(patient)
    response = recommendationAndTreat.diagnosis.manualDiagnosis + "\n >>>>TREATMENT:<<<<< \n" + recommendationAndTreat.treatmentPlan.treatment
    return Response(response, mimetype='text/plain')


@app.route("/recommendation/processepi", methods=["POST"])
def processPatientDataEpi():
    requestBody = request.data.decode("utf-8")
    patient = Patient(requestBody)
    recommendationAndTreat = recomendationService.generate_recommendation(patient)
    response = recommendationAndTreat.treatmentPlan.epicrisis
    return Response(response, mimetype='text/plain')


@app.route("/recommendation/processann", methods=["POST"])
def processPatientDataAnn():
    requestBody = request.data.decode("utf-8")
    patient = Patient(requestBody)
    recommendationAndTreat = recomendationService.generate_recommendation(patient)
    payload:Payload = recomendationService.performer._payload
    payload.annotationsGen
    return Response(payload.annotationsGen, mimetype='text/plain')


@app.route("/recommendation/datadef", methods=["GET"])
def showData():
    return Response(
        json.dumps(dict(zip(dataDefinitionEntries.keys(), list(map(objectify, list(dataDefinitionEntries.values())))))),
        mimetype='application/json')


@app.route("/recommendation/traceLog/<externalSessionId>", methods=["GET"])
def traceLog(externalSessionId):
    return Response(TraceLog().fetch(externalSessionId), mimetype='text/plain')


@app.route("/recommendation/traceLog/<externalSessionId>", methods=["POST"])
def addLog(externalSessionId):
    TraceLog().add(externalSessionId, request.data.decode("utf-8"))
    return Response("", mimetype='text/plain')


@app.route("/recommendation/traceLogAdd/<externalSessionId>", methods=["POST"])
def addLogPlain(externalSessionId):
    TraceLog().add(externalSessionId, request.data.decode())
    return Response("", mimetype='text/plain')


def objectify(dataDef):
    units = dataDef[3].split("|")
    unitsJoined = "|".join(map(lambda x: x.strip(), units))
    unitsStrippedOfFOrmulas = re.sub(r'\([^)]*\)', '', unitsJoined)
    unitsStrippedOfNorms = re.sub(r'\{[^}]*\}', '', unitsStrippedOfFOrmulas)
    return {"code": dataDef[0],
            "title": re.sub(r'\|[ ]*$', '', dataDef[1]).strip(),
            "type": dataDef[2],
            "unit": unitsStrippedOfNorms}


def saveJson(requestBody, prefix):
    text_file = open("request_response/" + prefix + time.strftime("%Y%m%d-%H%M%S") + ".json", "w")
    text_file.write((requestBody))
    text_file.close()


if __name__ == "__main__":
    print("Starting Recommedation server...")
    mps = RecommendationServer().run()
    print("Recommedation server  started.")
