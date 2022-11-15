from recommendation.classifiers.additionalDataVars import AdditionalDataVars
from recommendation.dataExtractors.MedicalDataRepository import MedicalDataRepository


class MedicalDataMapper(MedicalDataRepository):

    def __init__(self, payload) -> None:
        self.patientData = payload.patientData
        super().__init__(payload)

    def isolateData(self):
        # -1 niezainicjowane zmienna (nie znaleziono informacji o tej chorobie lub jej braku)
        # 0 brak choroby/symptomu
        # 1 jest choroba
        # inna wartość dodatnia - wartość właściwa dla danego badania

        AdditionalDataVars(self.payload, self.patientData).initData()
        ## dane pomiarowe

        self.patientData.cisnienie_skurczowe = getint(self.getIndispensableMedicalEntry("cisnienie_skurczowe"))
        self.patientData.cisnienie_rozkurczowe = getint(self.getIndispensableMedicalEntry("cisnienie_rozkurczowe"))
        self.patientData.cholesterol_calkowity = getint(self.getIndispensableMedicalEntry("cholesterol_calkowity"))
        self.patientData.eGFR = getfloat(self.getIndispensableMedicalEntry("eGFR"))  # (estimated glomerular filtration rate) - szacunkowy wspóczynnik filtracji kłębuszkowej - miara niewyd. nerek
        self.patientData.ddimery = getfloat(self.getOptionalMedicalEntry("D-dimery"))  # (estimated glomerular filtration rate) - szacunkowy wspóczynnik filtracji kłębuszkowej - miara niewyd. nerek
        self.patientData.ChSN = self.getOptionalMedicalEntry("ChSN")  # choroba s-n w badaniu obrazowym: istotne miażdżycowe zwężenie naczynia (?50#), rozpoznane angiograficznie lub ultrasonograficznie
        # nie obejmuje pogrubienia kompleksu błony wewnętrznej i środkowej tętnicy szyjne

        # dane wywiadu
        self.patientData.wiek = (getfloat(self.getIndispensableMedicalEntry("wiek")))
        self.patientData.age_in_days = getfloat(self.payload.patient.medicalData["age_in_days"])
        self.patientData.centile = getfloat(self.getOptionalMedicalEntry("centyl"))
        gender = self.getIndispensableMedicalEntry("plec")
        self.patientData.plec = 1 if (gender in {"żeńska", "zenska", "kobieta", "female", "FEMALE"}) else 0  # 1 - kobieta, 0 - mężczyzna

        self.patientData.palenie = self.getOptionalMedicalEntry("palenie")

        self.patientData.cukrzyca = self.getOptionalMedicalEntry("cukrzyca")  # cukrzyca 1 lub 2
        self.patientData.powiklania_narzadowe = self.getOptionalMedicalEntry(
            "powiklania_narzadowe")  # powikłania narządowe: 1-proteinuria (białkomocz)
        self.patientData.zaburzenia_lipidowe = self.getOptionalMedicalEntry(
            "zaburzenia_lipidowe")  # zaburzenia gospodarki lipidowej
        self.patientData.CKD = self.getOptionalMedicalEntry(
            "CKD")  # chronic kidney disease - przewlekła choroba nerek (PChN)
        self.patientData.ciaza = self.getOptionalMedicalEntry("ciaza")

        self.patientData.nadcis_przer_lkomory = self.getOptionalMedicalEntry(
            "nadcis_przer_lkomory")  # nadciśnieniowy przerost mięśnia lewej komory
        self.patientData.CAD = self.getOptionalMedicalEntry(
            "CAD")  # choroba wieńcowa: 1- przewlekła, 2- ostra (niestabilna), zawał #*****NiestChWien = 1 #niestabilna choroba wieńcowa, czyli ostra #OZaSerca = 1 #ostry zawał serca,
        self.patientData.rewaskularyzacja_wiencowa_lub_inna = self.getOptionalMedicalEntry(
            "rewaskularyzacja_wiencowa_lub_inna")  # rewaskularyzacja tętnicy wieńcowej lub innej
        self.patientData.choroba_tetnic_obwodowych = self.getOptionalMedicalEntry(
            "choroba_tetnic_obwodowych")  # choroba tętnic obwodowych
        self.patientData.tetniak_aorty = self.getOptionalMedicalEntry("tetniak_aorty")  # tętniak aorty
        self.patientData.udar = self.getOptionalMedicalEntry("udar")  # TIA-1, udar mózgu-2

        self.patientData.deprywacja = self.getOptionalMedicalEntry("deprywacja")
        self.patientData.otylosc = self.getOptionalMedicalEntry("otylosc")
        self.patientData.stres = self.getOptionalMedicalEntry("stres")
        self.patientData.rodzinne_CVD = self.getOptionalMedicalEntry("rodzinne_CVD")
        self.patientData.choroba_psychiczna = self.getOptionalMedicalEntry("choroba_psychiczna")
        self.patientData.HIV = self.getOptionalMedicalEntry("HIV")
        self.patientData.migotanie_przedsionkow = self.getOptionalMedicalEntry("migotanie_przedsionkow")
        self.patientData.przerost_lewej_komory = self.getOptionalMedicalEntry("przerost_lewej_komory")
        self.patientData.bezdech = self.getOptionalMedicalEntry("bezdech")
        self.patientData.aktywnosc_fizyczna = getint(
            self.getOptionalMedicalEntry("aktywnosc_fizyczna"))  # w jednostkach h/tydz.
        self.patientData.choroba_autoimmunologiczna = self.getOptionalMedicalEntry(
            "choroba_autoimmunologiczna")  # reumatoidalne zapalenie stawów, toczeń rumieniowaty układowy oraz łuszczyca

        self.patientData.klasa_nadcisn = self.getOptionalMedicalEntry("klasa_nadcisn")

        self.patientData.choroba_nerek = self.getOptionalMedicalEntry("choroba_nerek")
        self.patientData.CVD = self.getOptionalMedicalEntry("CVD")

        self.patientData.HMOD = self.getOptionalMedicalEntry("HMOD")  # ? co to
        self.patientData.ABPM = self.getOptionalMedicalEntry("ABPM")

        self.patientData.HFrEF = self.getOptionalMedicalEntry("HFrEF")  # -1
        self.patientData.choroba_wiencowa = self.getOptionalMedicalEntry(
            "choroba_wiencowa")  # rewaskularyzacja_wiencowa_lub_inna??
        self.patientData.zespol_kruchosci = self.getOptionalMedicalEntry("zespol_kruchosci")
        self.patientData.incydent_zakrzep_zator = self.getOptionalMedicalEntry("incydent_zakrzepowo_zatorowy")
        self.patientData.choroba_naczyniowa = self.getOptionalMedicalEntry("choroba_naczyniowa")
        self.patientData.LDL_C = getfloat(self.getIndispensableMedicalEntry("LDL")) # 80  # w jednostkach mg/dl


        # Contraindications related eGFR

    def isolateContraindicationsData(self):
        self.patientData.dna_moczanowa = self.getOptionalMedicalEntry("dna_moczanowa")  # 1
        self.patientData.zespol_metaboliczny = self.getOptionalMedicalEntry("zespol_metaboliczny")  # 0
        self.patientData.nietolerancja_glukozy = self.getOptionalMedicalEntry("nietolerancja_glukozy")  # 0
        self.patientData.hiperkalcemia = self.getOptionalMedicalEntry("hiperkalcemia")  # 0
        self.patientData.hipokaliemia = self.getOptionalMedicalEntry("hipokaliemia")  # -1
        self.patientData.astma = self.getOptionalMedicalEntry("astma")  # -1
        self.patientData.blok_zatokowo_przedsionkowy = self.getOptionalMedicalEntry("blok_zatokowo_przedsionkowy")  # -1
        self.patientData.blok_przedsionkowo_komorowy = self.getOptionalMedicalEntry("blok_przedsionkowo_komorowy")  # -1
        self.patientData.bradykardia = self.getOptionalMedicalEntry("bradykardia")  # -1
        self.patientData.dysfunkcja_LV = self.getOptionalMedicalEntry("dysfunkcja_LV")  # -1
        self.patientData.obrzek_naczynioruchowy = self.getOptionalMedicalEntry("obrzek_naczynioruchowy")  # -1
        self.patientData.stosowanie_srodkow_antykoncepcyjnych = self.getOptionalMedicalEntry(
            "stosowanie_srodkow_antykoncepcyjnych")  # -1
        self.patientData.obustronne_zwezenie_tetnic_nerkowych = self.getOptionalMedicalEntry(
            "obustronne_zwezenie_tetnic_nerkowych")  # 0
        self.patientData.zaparcia = self.getOptionalMedicalEntry("zaparcia")  # 1
        self.patientData.tachyarytmia = self.getOptionalMedicalEntry("tachyarytmia")  # -1
        self.patientData.niewydolnosc_serca = 1 if self.patientData.HFrEF > 0 else -1
        self.patientData.obrzek_konczyn_dolnych = self.getOptionalMedicalEntry("obrzek_konczyn_dolnych")  # 0
        self.patientData.hiperkaliemia = self.getOptionalMedicalEntry("hiperkaliemia")  # 0


def getint(param):
    return int(getfloat(param))


def getfloat(param):
    try:
        if (param != None and param != -1 and isinstance(param, str)):
            return float(param.replace(",", "."))
        if (param != None):
            return float(param)
        return param
    except:
        # -1 mean lack of data
        return -1