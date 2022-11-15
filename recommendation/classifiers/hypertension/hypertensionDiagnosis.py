from recommendation.classifiers.ScoreCalculator import calculate_SCORE
from recommendation.classifiers.hypertension.CHA2DS2_VASc import CHA2DS2_VASc
from recommendation.classifiers.hypertension.DutchLipidClinicNetworkScore import DutchLipidClinicNetworkScore
from recommendation.classifiers.hypertension.HAS_BLED import HAS_BLED
from recommendation.classifiers.hypertension.HypertensionClass import HypertensionClass
from recommendation.classifiers.hypertension.KDIGO import KDIGO
from recommendation.dataExtractors.dataDefinitions import dataDefinitionEntries
from recommendation.processStep.ExtractDataFromText import ExtractAdditionalDataFromText
from recommendation.processStep.GetDataOutOfNorms import GetDataOutOfNorms


class HypertensionDiagnosis(object):

    def __init__(self, payload, patientData) -> None:
        self.patientData = patientData
        self.payload = payload
        self.dataFromText = ExtractAdditionalDataFromText(self.payload, self.patientData)

    def generateDiagnosis(self):

        self.addLine('<b>Klasyfikacja wartości ciśnienia tętniczego/screening nadciśnienia:</b>')

        ## reguły dot. rozpoznania nadciśnienia str. 10/89 i 20/89??
        # skrining  nadciśnienia

        hypertensionClass = HypertensionClass()
        hypertensionCategory = hypertensionClass.determineClass(self.patientData.cisnienie_skurczowe, self.patientData.cisnienie_rozkurczowe)
        isIsolatedSystolic = hypertensionClass.isIsolatedSystolic(self.patientData.cisnienie_skurczowe, self.patientData.cisnienie_rozkurczowe)
        czestosc_pomiarow = ''
        if self.patientData.wiek > 50:
            czestosc_pomiarow = ' (rozważyć częstsze pomiary BP w gabinecie ze względu na szybszy wzrost SBP wraz z wiekiem)'

        if isIsolatedSystolic:
            self.patientData.klasa_nadcisn = 8
            self.addLine('- izolowane NT skurczowe{}'.format(czestosc_pomiarow))
        elif hypertensionCategory == -2:
            self.patientData.klasa_nadcisn = 1
            self.addLine('- optymalne, nastepny pomiar za 5 lat lub wcześniej{}'.format(czestosc_pomiarow))
        elif hypertensionCategory == -1:
            self.patientData.klasa_nadcisn = 3
            self.addLine('- prawidłowe, nastepny pomiar za 3 lata lub wcześniej{}'.format(czestosc_pomiarow))
        elif hypertensionCategory == 0:
            self.patientData.klasa_nadcisn = 4
            self.addLine('- wysokie prawidłowe, nastepny pomiar za rok lub wcześniej{}.'.format(czestosc_pomiarow))
        elif hypertensionCategory == 1:
            self.patientData.klasa_nadcisn = 5
            self.addLine('- Nadciśnienie Tętnicze 1. stopnia. <br>\t Porada dot. zmian stylu życia. Farmakoterapia, gdy po 3-6 miesiącach od interwencji dot. zmian stylu życia BP jest źle kontrolowane. W przypadku wysokiego ryzyka sercowo-naczyniowego leczenie rozpocząć natychmiast.')
        elif hypertensionCategory == 2:
            self.patientData.klasa_nadcisn = 6
            self.addLine('- Nadciśnienie Tętnicze 2. stopnia.  <br>\t Modyfikacja stylu życia, leczenie rozpocząć natychmiast')
        else:
            # hypertensionCategory == 3:
            self.patientData.klasa_nadcisn = 7
            self.addLine('- Nadciśnienie Tętnicze 3. stopnia.  <br>\t Modyfikacja stylu życia, leczenie rozpocząć natychmiast')  # self.patientData.cisnienie_skurczowe >= 180 or self.patientData.cisnienie_rozkurczowe >=110
        if self.patientData.klasa_nadcisn == 4:
            self.addLine('  Rozważ maskowane nadciśnienie tętnicze.')
            self.addLine('  Rozważ pomiary ciśnienienia tętniczego poza gabinetem lekarskim (ABPM lub HBPM).')
        elif self.patientData.klasa_nadcisn >= 5 and self.patientData.ABPM == -1:
            self.addLine(
                '  Wskazana powtórna wizyta z pomiarami BP w gabinecie lub poza gabinetem (ABPM lub HBPM).')
        ## ocena ryzyka sercowo-naczyniowego

        score = calculate_SCORE(self.patientData.plec, self.patientData.wiek, self.patientData.palenie, self.patientData.cisnienie_skurczowe,
                                self.patientData.cholesterol_calkowity)
        # Jaki region pochodzenia?
        score = score * self.patientData.region_pochodzenia_pacjenta
        self.addLine('')
        self.addLine("<b>Systematic Coronary Risk Evaluation (SCORE) : </b>{} ".format(score))
        # Ocena ryzyka sercowo-naczyniowego - kategoryzacja ryzyka
        self.addLine('<b> Ocena ryzyka sercowo-naczyniowego - kategoryzacja ryzyka: </b>')
        if (score >= 10) or ((self.patientData.eGFR < 30) or (
                self.patientData.cukrzyca > 0 and (
                self.patientData.powiklania_narzadowe > 0 or self.patientData.klasa_nadcisn == 7 or self.patientData.zaburzenia_lipidowe == 1))) or (
                self.patientData.CAD > 0 or self.patientData.rewaskularyzacja_wiencowa_lub_inna or self.patientData.udar > 0 or self.patientData.tetniak_aorty or self.patientData.choroba_tetnic_obwodowych):
            self.patientData.ryzyko = 3
            self.addLine('- ryzyko bardzo wysokie')
        elif (score >= 5) and (score < 10) or self.patientData.nadcis_przer_lkomory or (
                self.patientData.cholesterol_calkowity > 310) or (
                self.patientData.klasa_nadcisn == 7) or (
                self.patientData.cukrzyca > 0 and ~((self.patientData.cukrzyca == 1) and (self.patientData.wiek <= 30))) or (
                60 > self.patientData.eGFR) and (self.patientData.eGFR >= 30):
            self.patientData.ryzyko = 2
            self.addLine('- ryzyko wysokie')
        elif (score >= 1) and (score < 5) or self.patientData.klasa_nadcisn == 6:
            self.patientData.ryzyko = 1
            self.addLine('- ryzyko umiarkowane')
        else:
            self.patientData.ryzyko = 0
            self.addLine('- ryzyko niskie')  # score < 1,
        # czynniki modyfikujące ryzyko oszacowane za pomocą skali SCORE

        self.addLine('')
        self.addLine('<b>Kliniczne prawdopodobieństwo rozpoznania hipercholesterolemii rodzinnej (FH) -  The Dutch Lipid Clinic Network:</b>')

        dutchLipidClinicNetworkScore = DutchLipidClinicNetworkScore(self.payload, self.patientData)
        dutchLipidClinicNetworkScoreVal, source = dutchLipidClinicNetworkScore.calculateFromPatientData()

        self.addLine('\twynik: ' + str(dutchLipidClinicNetworkScoreVal))
        self.addLine('\tuwzględnione czynniki: ' + str(source).replace("'", "`"))

        if self.patientData.migotanie_przedsionkow == 1 or (self.dataFromText.checkAdHocTextR(".igotani.{0,10} przeds.{0,20}", "migotanie_przedsionkow") > 0):
            self.addLine('<br><b><u>Migotanie przedsionków:</u> </b>')
            self.addLine('')
            self.addLine('<b>Skala HAS-BLED (skala krwawień Birmingham) :</b>')
            hasBled = HAS_BLED(self.payload, self.patientData)
            hasBledVal, source = hasBled.calculateFromPatientData()

            self.addLine('\twynik: ' + str(hasBledVal))
            self.addLine('\tuwzględnione czynniki: ' + str(source).replace("'", "`"))

            self.addLine('')
            self.addLine('<b>CHA<sub>2</sub>DS<sub>2</sub>–VASc:</b>')
            #  self.patientData.nadcis_przer_lkomory    self.patientData.przerost_lewej_komory

            cHA2DS2_VASc = CHA2DS2_VASc(self.payload, self.patientData)
            cHA2DS2_VAScVal, source = cHA2DS2_VASc.calculateFromPatientData()

            self.addLine('\twynik: ' + str(cHA2DS2_VAScVal))
            self.addLine('\tuwzględnione czynniki: ' + str(source).replace("'", "`"))

            vTexts = cHA2DS2_VASc.getText(cHA2DS2_VAScVal, self.patientData.plec)
            # {"ryzyko": "niskie", "Leczenie_przeciwzakrzepowe": "Nie zaleca się", "leki": "Brak leczenia"}
            self.addLine('\t\tRyzyko: ' + vTexts["ryzyko"])
            self.addLine('\t\tLeczenie przeciwzakrzepowe: ' + vTexts["Leczenie_przeciwzakrzepowe"])
            self.addLine('\t\tLeki: ' + vTexts["leki"])

        self.addLine('')

        unitDefinitions = dataDefinitionEntries["eGFR"][3]
        age_in_days = self.payload.patientData.age_in_days
        gender = "F" if self.payload.patientData.plec == 1 else "M"
        centile = self.payload.patientData.centile
        age_in_years = int(age_in_days / 365)
        eGFRnotInNorms, norm =  GetDataOutOfNorms().valueNotInNorms(age_in_days, age_in_years, gender, centile, unitDefinitions, self.patientData.eGFR)

        if eGFRnotInNorms or self.patientData.CKD > 0 or self.patientData.choroba_nerek > 0:
            self.addLine('<b>Stadia przewlekłej niewydolności nerek wg KDIGO :</b>')

            vKDIGO = KDIGO(self.payload, self.patientData)
            vKDIGOVal, source = vKDIGO.calculateFromPatientData()

            self.addLine('\twynik: ' + str(vKDIGOVal))
            self.addLine('\tuwzględnione czynniki: ' + str(source).replace("'", "`"))

        risktxt = ""
        if self.patientData.deprywacja > 0:
            risktxt += ('- Wykluczenie społeczne - źródło wielu przyczyn CVD<br>')
        if self.patientData.otylosc > 0:
            risktxt += ('- Otyłość i otyłość centralna<br>')
        if self.patientData.aktywnosc_fizyczna == 0:
            risktxt += ('- Brak aktywności fizycznej<br>')
        if self.patientData.stres > 0:
            risktxt += ('- Długotrwały stres, w tym zespół wypalenia<br>')
        if self.patientData.rodzinne_CVD > 0:
            risktxt += ('- Wywiad rodzinny przedwczesnej CVD (mężczyźni: < 55 lat; kobiety: < 60 lat)<br>')
        if self.patientData.choroba_autoimmunologiczna > 0:
            risktxt += ('- Choroby autoimmunologiczne i zapalne<br>')
        if self.patientData.choroba_psychiczna > 0:
            risktxt += ('- Poważne choroby psychiczne<br>')
        if self.patientData.HIV > 0:
            risktxt += ('- Leczenie zakażenia ludzkim wirusem upośledzenia odporności<br>')
        if self.patientData.migotanie_przedsionkow > 0:
            risktxt += ('- Migotanie przedsionków<br>')
        if self.patientData.przerost_lewej_komory > 0:
            risktxt += ('- Przerost lewej komory<br>')
        if self.patientData.CKD > 0:  # sprawdzić!!
            risktxt += ('- Przewlekła choroba nerek<br>')
        if self.patientData.bezdech > 0:
            risktxt += ('- Zespół obturacyjnego bezdechu sennego<br>')
        if risktxt != "":
            self.addLine('<br>Występują następujące czynniki modyfikujące ryzyko:')  # str. 15/85
            self.addLine(risktxt)

    def addLine(self, line):
        self.payload.diagnosis.manualDiagnosis += line + "<br>"
