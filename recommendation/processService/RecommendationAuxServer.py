import json
import logging
import os
import re
import threading
import time

from flask import Flask, Response
from gevent.pywsgi import WSGIServer

from recommendation.aux.service.TraceLog import TraceLog
from recommendation.dataExtractors.dataDefinitions import dataDefinitionEntries

logging.basicConfig(level=logging.INFO)

VERSION = "0.4"

#####################################################################################

app = Flask(__name__)


#####################################################################################

class RecommendationAuxServer():
    jsonSchemes = {}

    def runHttpServer(self, serverIp):
        httpServer = WSGIServer((serverIp, 1111), app)
        httpServer.serve_forever()

    def run(self):
        os.environ['FLASK_RUN_PORT'] = "1111"
        t = threading.Thread(target=self.runHttpServer, args=("0.0.0.0",))
        t.daemon = True
        print("Starting HTTP recommendation aux server...")
        t.start()
        print("HTTP server started.")
        while (True):
            time.sleep(0.001)


def objectify(dataDef):
    return {"code": dataDef[0],
            "title": dataDef[1],
            "type": dataDef[2],
            "unit": re.sub(r'\([^)]*\)', '', dataDef[3])}


@app.route("/recommendation_old/datadef", methods=["GET"])
def showData():
    return Response(json.dumps(dict(zip(dataDefinitionEntries.keys(), list(map(objectify, list(dataDefinitionEntries.values())))))), mimetype='application/json')

@app.route("/recommendation/traceLog/<externalSessionId>", methods=["GET"])
def traceLog(externalSessionId):
    return Response(TraceLog().fetch(externalSessionId), mimetype='text/plain')

@app.route("/recommendation/traceLogAll/<externalSessionId>", methods=["GET"])
def traceLogAll(externalSessionId):
    return Response(TraceLog().fetchAll(externalSessionId), mimetype='text/html')

@app.route("/recommendation/traceLogAll/traceItem/<externalSessionId>/<timestamp>", methods=["GET"])
def traceItem(externalSessionId, timestamp):
    return Response(TraceLog().fetchRecord(externalSessionId, timestamp), mimetype='text/html')

if __name__ == "__main__":
    print("Starting Recommedation Aux server...")
    mps = RecommendationAuxServer().run()
    print("Recommedation server Aux started.")
