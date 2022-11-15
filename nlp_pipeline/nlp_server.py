import os
import shutil
import socket
import sys
import this
import spacy
import datetime
import queue
import time
import threading
import traceback


from db_server import PIPELINE_NLP_FOLDER, PIPELINE_WORK_FOLDER, PIPELINE_WORK_RESULTS_FOLDER
from nlp_pipeline.json_exporter import JSONExporter
from nlp_pipeline.nlp_pipeline import NLPPipeline
from recommendation.aux.service.TraceLog import TraceLog

op_codes = ["PING", "LOCAL_REQUEST", "NETWORK_REQUEST", "TRAIN", "STATISTICS", "LOCAL_STATUS", "NETWORK_STATUS",
            "SHUTDOWN", "PROCESSALL"]

answers = ["OK", "PENDING", "FAILED"]

processingLock = threading.Lock()
# Listener komunikuje się z Processorem i na odwrót poprzez klasę NLPServer i kolejki komunikatów

class NLPServerMessage():
    conn = None
    type = ""
    op = ""
    data = ""
    guid = ""

    def __init__(self, conn0, type0, op0, data0):
        self.conn = conn0
        self.type = type0
        self.op = op0
        self.data = data0
        self.guid = None
        pass

    # nlpSrv.thr_processor.putSysMsg(nlp_pipeline.nlp_server.NLPServerMessage(None,"INCOMING_OP", "LOCAL_REQUEST",
    # request.data, guid))

    def __init__(self, conn0, type0, op0, data0, guid0):
        self.conn = None
        self.type = type0
        self.op = op0
        self.data = data0
        self.guid = guid0
        pass


class NLPServerThread(threading.Thread):
    messages = queue.LifoQueue()

    def putSysMsg(self, msg):
        self.messages.put(msg)


class NLPServer():

    #    main_case_document
    #    annotation_pipe_output
    #    recommendation_output
    #    risks_output
    #
    #
    #    Do każdego dokumentu trzeba będzie przygotować operacje CRUD rest
    #    dla użytku poszczególnych modułów, w szczególności (w zarysie):
    #
    # add/getPatient(), add/getAnnotation(), add/getDiagnosis(), add/getTreatmentPlan(),
    # get/addaddMedicalData(),updateMedicalData(), // wyniki badań
    # get/AddRisk()

    bRunningLock = threading.Lock()
    bRunning = True

    pipeline = None

    pipelineStatusLock = threading.Lock()
    pipelineStatus = None  # For network requests
    pipelineCurrentGUID = None  # Current GUID for local request - statuses below
    pipelineStatuses = {}  # dict of { guid, status }

    thrListener = None
    thrProcessor = None

    serverHost = "127.0.0.1"
    serverPort = 20000

    requests = []

    nlp = None

    mongoClient = None

    def getRequestGuid(self):

        s_date_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")

        return s_date_time

    def nlpLog(self, s):

        now = datetime.datetime.now()
        log_s = "[" + str(now) + "]: " + s
        print(log_s)

    def __init__(self, mongoClient0):

        self.mongoClient = mongoClient0

        self.nlpLog("Starting MediPlanner NLP Server...")

        self.boot()

        self.nlpLog("MediPlanner NLP Server started.")

    def boot(self):

        self.nlpLog("Loading pl_spacy_model...")
        nlp = spacy.load('pl_spacy_model')
        self.nlpLog("pl_spacy_model loaded.")

        self.nlpLog("Starting pipeline...")
        self.pipeline = NLPPipeline(nlp)
        self.nlpLog("Pipeline started.")

        # Todo: Include in boot?:
        # selectedMeshPolTags = list(map(lambda line: self.pipeline.mc.MeshPolTag(line), self.pipeline.mc.linesFromFile("crf/conversion/distinctMeshPolTags.txt")))
        # meshPols = self.pipeline.mc.getMeshPols(True, "crf/conversion/meshpol.tsv", selectedMeshPolTags, "crf/conversion/meshpol_cache.json")
        # medicines = self.pipeline.mc.getMedicines(True, "crf/conversion/rpo.tsv", "crf/conversion/medicines_cache.json")

    def shutdown(self):

        self.nlpLog("Shutting server down...")

        self.thrListener.putSysMsg(NLPServerMessage(None, "SHUTDOWN", None, None))

        self.thrProcessor.join()
        self.thrListener.join()

        # Clear working directories here?

        self.nlpLog("Server shut down.")

    def pipelineProcess(self, s_data, cnn_0):

        print("Entering request processor thread...")

        self.pipeline.process_text(s_data, False, "")

        print("Putting SysMsg from request processor thread...")

        self.thrProcessor.putSysMsg(NLPServerMessage(cnn_0, "NETWORK_REQUEST_FINISHED", "PROCESS", None, None))


    def pipelineLocalProcess(self, s_data, guid): # without remote connectione

        print("Entering request processor thread...")

        self.pipelineCurrentGUID = guid
        self.pipelineStatuses[guid] = "PENDING"

        baseDir = os.getcwd()

        print("pipelineLocalProcess() CWD = " + baseDir)
        json_file = PIPELINE_WORK_RESULTS_FOLDER + "/" + guid + "_fallback.json"
        TraceLog().add("lock", "reading "+ json_file)
        f = open(json_file, "w", encoding="utf-8")
        f.write("{ \"annotations\":[ {} ], \"originalText\": \"" + s_data.replace("\"", " ").replace("\n","\\n")+"\"}")
        f.close()

        #  acquire lock
        TraceLog().add("lock", "processingLocks before" )
        os.chdir(PIPELINE_NLP_FOLDER)

        self.pipeline.process_text(s_data, False, guid)  # TODO: Instead of calling directly in db_server - send appropriate msg to nlp_server in db_server
        print("Putting SysMsg from request processor thread...")

        self.thrProcessor.putSysMsg(NLPServerMessage(None, "LOCAL_REQUEST_FINISHED", "PROCESS", None, guid))


        TraceLog().add("lock", "processingLocks after")
        os.chdir(baseDir)

    def pipelineProcessAll(self, s_data, cnn_0, thr_process_0):

        print("Entering request all processor thread...")

        self.pipeline.process("all", False, "pipelineProcessAll")

        print("Putting SysMsg from request all processor thread...")

        thr_process_0.putSysMsg(NLPServerMessage(cnn_0, "NETWORK_REQUEST_FINISHED", "PROCESS_ALL", None, None))

    def pipelineTrain(self, s_data, cnn_0, thr_process_0):

        print("Entering train processor thread...")

        self.pipeline.train("all")

        print("Putting SysMsg from train processor thread...")

        thr_process_0.putSysMsg(NLPServerMessage(cnn_0, "NETWORK_REQUEST_FINISHED", "TRAIN", None, None))

    def getRequestStatus(self, guid):

        self.pipelineStatusLock.acquire()
        s = self.pipelineStatuses[guid]
        self.pipelineStatusLock.release()

        return s

    def getRequestResult(self, guid):

        s = ""

        try:
            if os.path.isdir("results/" + guid):
                f = open("results/" + guid + "/tmp_input.json", "r", encoding="utf-8")
                s = f.read()
            else:
                pass # s = ""
        except Exception as e:
            pass  # todo

        return s

    # obsolete - todo: remove
    def setPipelineStatus(self, s):

        self.pipelineStatusLock.acquire()
        self.pipelineStatus = s
        self.pipelineStatusLock.release()

    def nlpServerProcessor(self):

        je = JSONExporter()

        print("Server processor started.")

        b_running = True
        while b_running:
            time.sleep(0.001)
            if not self.thrProcessor.messages.empty():
                # print("Getting processor message...")
                msg = self.thrProcessor.messages.get()
                opcode = msg.op
                s_data = msg.data
                s_guid = msg.guid
                cnn = msg.conn
                self.thrProcessor.messages.task_done()
                if msg.type == "NETWORK_REQUEST_FINISHED":

                    if opcode == "PROCESS":

                        # f = open("work/test_output_attributes/tmp_input.ann", "r", encoding="utf-8", errors='ignore')
                        # out_s = f.readlines()
                        # f.close()

                        s_json = je.convert("work/test_output_attributes/tmp_input.ann", "tmp_input.txt",
                                            "work/test_output_attributes/tmp_input.json")
                        print("Sending result JSON...")
                        cnn.sendall(bytearray(s_json, "utf-8"))
                        cnn.close()
                        self.setPipelineStatus("READY")

                    elif opcode == "PROCESS_ALL":

                        cnn.sendall(bytearray("Finished", "utf-8"))
                        cnn.close()
                        self.setPipelineStatus("READY")

                    elif opcode == "TRAIN":

                        cnn.sendall(bytearray("OK", "utf-8"))
                        cnn.close()
                        self.setPipelineStatus("READY")

                elif msg.type == "LOCAL_REQUEST_FINISHED":

                    # Save result by GUID

                    if opcode == "PROCESS":

                        guid = s_guid

                        # Copy result to guid directory

                        baseDir = os.getcwd()
                        os.chdir(PIPELINE_WORK_FOLDER)

                        if not os.path.isdir("results/" + guid):
                            os.mkdir("results/" + guid)

                        s_json = je.convert("test_output_attributes/tmp_input.ann", "tmp_input.txt",
                                            "test_output_attributes/tmp_input.json")
                        f = open("results/" + guid + "/tmp_input.json", "w", encoding="utf-8")
                        f.write(s_json)
                        f.close()
                        shutil.copy("test_output_attributes/tmp_input.json", "results/" + guid)

                        i_dict = {'guid' : guid, 'jsonResult' : s_json }

                        # {
                        #     "text_id": "<ObjectId1>",
                        #     "date": "<date>",
                        #     "pipeVersion": "<String>",
                        #     "annotations": {
                        #         {anotacja1}, {anotacja2}, ... // jak w poprzednich ustaleniach
                        #     },
                        #     "originalText": "originalText"
                        # }

                        db = self.mongoClient.get_database("main")
                        insertResult = db["annotations"].insert_one(i_dict)
                        #result = str(insert_result.inserted_id)

                        self.pipelineStatusLock.acquire()
                        self.pipelineStatuses[guid] = "OK"
                        self.pipelineStatusLock.release()

                        os.chdir(baseDir)

                elif msg.type == "INCOMING_OP":

                    # nlpSrv.thr_processor.putSysMsg(
                    #    nlp_pipeline.nlp_server.NLPServerMessage(None, "INCOMING_OP", "LOCAL_REQUEST",
                    #    request.data, guid))

                    if opcode == "LOCAL_REQUEST":  # From db_server

                        # self.set_pipeline_status("BUSY")

                        self.pipelineStatusLock.acquire()
                        self.pipelineStatuses[s_guid] = "PENDING"
                        self.pipelineStatusLock.release()

                        try:
                            print("Starting local request processor thread...")

                            thr_process = threading.Thread(target=self.pipelineLocalProcess, args=(s_data, s_guid))
                            thr_process.run()

                        except Exception as e:
                            TraceLog().add(s_guid, "Pipeline request error: " + str(e))
                            self.nlpLog("Pipeline request error: " + str(e))
                            print(traceback.format_exc())

                    elif opcode == "REQUEST":

                        self.setPipelineStatus("PENDING")

                        try:
                            print("Starting network request processor thread...")

                            thr_process = threading.Thread(target=self.pipelineProcess,
                                                           args=(s_data, cnn, self.thrProcessor))
                            thr_process.run()

                        except Exception as e:
                            TraceLog().add(s_guid, "Pipeline request error 2: " + str(e))
                            self.nlpLog("Pipeline request error: " + str(e))
                            print(traceback.format_exc())
                            cnn.sendall(bytearray("ERROR", "utf-8"))
                            cnn.close()

                    elif opcode == "PROCESSALL":

                        self.setPipelineStatus("PENDING")

                        try:
                            print("Starting request all processor thread...")
                            thr_process = threading.Thread(target=self.pipelineProcessAll,
                                                           args=(s_data, cnn, self.thrProcessor))
                            thr_process.run()

                        except Exception as e:
                            TraceLog().add(s_guid, "Pipeline request all error: " + str(e))
                            self.nlpLog("Pipeline request all error: " + str(e))
                            print(traceback.format_exc())
                            cnn.sendall(bytearray("ERROR", "utf-8"))
                            cnn.close()

                    elif opcode == "TRAIN":

                        self.setPipelineStatus("PENDING")

                        try:
                            print("Starting train processor thread...")
                            thr_process = threading.Thread(target=self.pipelineTrain,
                                                           args=(s_data, cnn, self.thrProcessor))
                            thr_process.run()

                        except Exception as e:
                            TraceLog().add(s_guid, "Pipeline train error: " + str(e))

                            self.nlpLog("Pipeline train error: " + str(e))
                            print(traceback.format_exc())
                            cnn.sendall(bytearray("ERROR", "utf-8"))
                            cnn.close()

                        cnn.sendall(bytearray("OK", "utf-8"))

                        self.setPipelineStatus("READY")

                    elif opcode == "PING":

                        cnn.sendall(bytearray("PONG", "utf-8"))
                        cnn.close()

                    elif opcode == "LOCAL_STATUS":
                        # self.pipelineStatusLock.acquire()
                        # s_status = self.pipelineStatus
                        # self.pipelineStatusLock.release()

                        pass

                    elif opcode == "NETWORK_STATUS":

                        self.pipelineStatusLock.acquire()
                        s_status = self.pipelineStatus
                        self.pipelineStatusLock.release()

                        cnn.sendall(bytearray(s_status, "utf-8"))
                        cnn.close()

                    elif opcode == "STATISTICS":

                        s_stat = ""
                        for req in self.requests:
                            s_stat = s_stat + "[" + str(req[0]) + ", " + req[1] + "]\n"

                        cnn.sendall(bytearray(s_stat, "utf-8"))
                        cnn.close()

                    elif opcode == "SHUTDOWN":

                        cnn.sendall(bytearray("OK", "utf-8"))  # May be busy
                        cnn.close()

                        b_receive = False
                        b_running = False

                        self.thrListener.putSysMsg(NLPServerMessage(None, "SHUTDOWN", None, None))

                        self.bRunningLock.acquire()
                        self.bRunning = False
                        self.bRunningLock.release()

                    else:

                        cnn.sendall(bytearray("Unknown opcode " + opcode, "utf-8"))
                        cnn.close()

                # cnn.close() # Nie można z góry zamykać wszystkich cnn tutaj z powodu ReqProcessorThread

    def nlpServerListener(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.serverHost, self.serverPort))

        b_running = True
        while b_running:

            time.sleep(0.001)

            if not self.thrListener.messages.empty():
                # print("Incoming listener message...")
                msg = self.thrListener.messages.get()
                if msg.type == "SHUTDOWN":
                    # print("Listener shutdown...")
                    self.thrListener.messages.task_done()
                    return

            self.nlpLog("Listening on socket...")

            s.listen()
            conn, addr = s.accept()

            self.nlpLog('Connected by ' + str(addr))

            b_receive = True
            while b_receive:
                try:
                    data = conn.recv(32768)
                except:
                    b_receive = False

                if b_receive and len(data) > 0:
                    self.nlpLog("Processing incoming data...")

                    s_in = str(data, "utf-8")

                    opcode = s_in[0:10].strip()
                    s_data = s_in[11:]

                    self.nlpLog("OpCode = [" + opcode + "]")

                    now = datetime.datetime.now()
                    self.requests.append([now, opcode])

                    self.nlpLog("Putting SysMsg with incoming data...")

                    self.thrProcessor.putSysMsg(NLPServerMessage(conn, "INCOMING_OP", opcode, s_data))

                    self.nlpLog("SysMsg put.")

    def run(self):

        self.thrListener = NLPServerThread(target=self.nlpServerListener)
        self.thrProcessor = NLPServerThread(target=self.nlpServerProcessor)

        # -----------------------------------------------------------------

        self.thrListener.start()
        self.thrProcessor.start()

        # -----------------------------------------------------------------

        self.thrListener.join()
        self.thrProcessor.join()

        # -----------------------------------------------------------------

        self.shutdown()


if __name__ == "__main__":
    cnt = len(sys.argv)
    if cnt == 1:
        srv = NLPServer()
        srv.run()
