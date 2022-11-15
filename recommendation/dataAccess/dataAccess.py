import datetime

from recommendation.dataAccess.dbConnection import session
from recommendation.model.dbModels import DBPatient, DBPatientData, CallTrace


class DataAccess():

    def __init__(self) -> None:
        pass

    def getData(self, patientId, datum):
        return getattr(session.query(DBPatient).filter_by(patientId=patientId).one_or_none(), datum, None)

    def getExtendedData(self, patientId, datum):
        result = session.query(DBPatientData).filter_by(patientId=patientId)
        return getattr(result.one_or_none(), datum, None)

    def getTraceLog(self, externalSessionId):
        then = datetime.datetime.now() - datetime.timedelta(minutes=40)
        result = session.query(CallTrace).filter(CallTrace.externalSessionId == externalSessionId, CallTrace.created >= then).order_by(CallTrace.created).all()
        return "<h2>Log of " + externalSessionId + ":</h2><br>" + self.formatLog(result, externalSessionId)

    def getTraceLogAll(self, externalSessionId):
        result = session.query(CallTrace).filter(CallTrace.externalSessionId == externalSessionId).order_by(CallTrace.created).all()
        return self.formatLog(result, externalSessionId)

    def formatLog(self, result, externalSessionId):
        out = ""
        for item in result:
            out += "<a href='traceItem/" + externalSessionId + "/" + str(item.created.isoformat()) + "' target='_blank'>" + (str(item.created) + "</a>: " + item.log.replace("\n", " ")[0:150] + "<br>")
        return out

    def addTraceLog(self, externalSessionId, log):
        now = datetime.datetime.now()
        callTrace = CallTrace(log=log, externalSessionId=externalSessionId, created=now)
        session.add(callTrace)
        session.commit()

    def fetchRecord(self, externalSessionId, timestamp):
        then = datetime.datetime.fromisoformat(timestamp)
        result = session.query(CallTrace).filter(CallTrace.externalSessionId == externalSessionId, CallTrace.created == then).one_or_none()
        return result
