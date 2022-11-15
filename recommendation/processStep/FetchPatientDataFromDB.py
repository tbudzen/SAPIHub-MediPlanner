from recommendation.dataAccess.dataAccess import DataAccess
from recommendation.dataExtractors.MedicalDataRepository import nodata
from recommendation.dataExtractors.dataMap import dbExtendedDataMap, dbPatientDataMap
from recommendation.processStep.ProcessStep import ProcessStep


class FetchPatientDataFromDB(ProcessStep):

    def getStepIdentification(self):
        return "FetchPatientDataFromDB"

    def perform(self, payload) -> None:
        payload.status = "FetchPatientDataFromDB"
        dataAccess = DataAccess()
        try:
            patientId = int(payload.patient.patientIdentifier)
            for entry in dbExtendedDataMap:
                if nodata(payload.patient.medicalData, entry):
                    payload.patient.medicalData[entry] = dataAccess.getExtendedData(patientId, dbExtendedDataMap[entry])
            for entry in dbPatientDataMap:
                if nodata(payload.patient.medicalData, entry):
                    payload.patient.medicalData[entry] = dataAccess.getData(patientId, dbPatientDataMap[entry])
        except ValueError:
            # string identifier, not within the test db scope
            pass
        except TypeError:
            # string identifier, not within the test db scope
            pass
