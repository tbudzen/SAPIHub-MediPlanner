from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class DBPatient(base):
    __tablename__ = 'patientData'
    patientId = Column(Integer, primary_key=True)
    stayId = Column(String)
    unit = Column(String)
    doctorId = Column(String)
    dataType = Column(String)
    dateIn = Column(String)
    dateOut = Column(String)
    age = Column(String)
    gender = Column(String)
    icd9 = Column(String)
    icd10 = Column(String)
    entryDate = Column(String)
    entryName = Column(String)
    entryText = Column(String)


class DBPatientData(base):
    __tablename__ = 'patient_pressure'
    patientId = Column(String, primary_key=True)
    identyfikator_pobytu = Column(String)
    jednostka_pobytu = Column(String)
    identifikator_lek_wpr = Column(String)
    typ_wprowadzanych_danych = Column(String)
    data_pocz_pob = Column(String)
    data_konc_pob = Column(String)
    wiek = Column(String)
    gender = Column(String)
    icd9 = Column(String)
    icd10 = Column(String)
    data_wpisu = Column(String)
    nazwa_wpisu = Column(String)
    dane_wpisu = Column(String)
    height = Column(String)
    weight = Column(String)
    mass = Column(String)
    saturation = Column(String)
    hsds = Column(String)
    headcircumference = Column(String)
    systole = Column(String)
    diastole = Column(String)
    centyle = Column(String)
    bmi = Column(String)
    temp = Column(String)


class CallTrace(base):
    __tablename__ = 'callTrace'
    id = Column(Integer, primary_key=True)
    externalSessionId = Column(String)
    created = Column(TIMESTAMP)
    log = Column(String)
