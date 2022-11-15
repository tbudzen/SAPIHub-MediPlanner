from recommendation.classifiers.ScoreCalculator import calculate_SCORE
from recommendation.dataExtractors.MedicalDataRepository import MedicalDataRepository


class LipidClassifier(MedicalDataRepository):

    def __init__(self, payload, patientData) -> None:
        super().__init__(payload)
        self.patientData = patientData

    def classify(self):
        udokumentowana_CVD = self.getOptionalMedicalEntry(
            "udokumentowana_CVD")  # 0  # choroba układu sercowo-naczyniowego (przebyty zawał serca, ostry zespół wieńcowy, rewaskularyzacja wieńcowa (PCI lub CABG) i inne zabiegi rewaskularyzacji tętnic, udar mózgu/TIA oraz choroba tętnic obwodowych, blaszki miażdżycowe w koronografii lub ultrasonografii tętnic szyjnych)
        cukrzyca = self.getOptionalMedicalEntry("cukrzyca")  # 0  # cukrzyca 1 lub 2
        powiklania_narzadowe = self.getOptionalMedicalEntry(
            "powiklania_narzadowe")  # 0  # powikłania narządowe: 1-proteinuria (białkomocz)
        palenie = self.getOptionalMedicalEntry("palenie")  # 1
        nadcisnienie_tetnicze = self.getOptionalMedicalEntry("nadcisnienie_tetnicze")  # 0
        zaburzenia_lipidowe = self.getOptionalMedicalEntry(
            "zaburzenia_lipidowe")  # 0  # kępek żółtych, żółtaków powiek i przedwcześnie występującego rąbka starczego rogówki
        # (w wieku < 45 lat), a zwłaszcza rodzinnej hipercholesterolemii (FH)

        CKD = self.getOptionalMedicalEntry("CKD")  # 20  # przewlekła choroba nerek w jednostkach ml/min/1,73 m^2

        cholesterol_calkowity = self.patientData.cholesterol_calkowity  # 8  # w jednostkach mmol/l (310 mg/dl) #całkowity?!
        cisnienie_skurczowe = self.patientData.cisnienie_skurczowe  # 180  # w jednostkach mm Hg
        cisnienie_rozkurczowe = self.patientData.cisnienie_rozkurczowe  # 110  # w jednostkach mm Hg

        plec = self.getOptionalMedicalEntry("plec")  # 0  # 1 - kobieta, 0 - mężczyzna
        wiek = self.getOptionalMedicalEntry("wiek")  # 70
        choroba_autoimmunologiczna = self.getOptionalMedicalEntry(
            "choroba_autoimmunologiczna")  # 0  # reumatoidalne zapalenie stawów, toczeń rumieniowaty układowy oraz łuszczyca
        LDL_C = self.patientData.LDL_C  # 80  # w jednostkach mg/dl
        HDL_C = self.getOptionalMedicalEntry("HDL")  # 0.8  # w jednostkach mmol/l - jak modyfikować SCORE?

        odzywianie_sie = self.getOptionalMedicalEntry("odzywianie_sie")  # 0
        aktywnosc_fizyczna = self.getOptionalMedicalEntry("aktywnosc_fizyczna")  # 2.5  # w jednostkach h/tydz.
        BMI = self.getOptionalMedicalEntry("BMI")  # 21  # w kg/m^2
        obwod_pasa = self.getOptionalMedicalEntry("obwod_pasa")  # 80
        cukrzyca_HbA = self.getOptionalMedicalEntry("cukrzyca_HbA")  # 53

        deprywacja = self.getOptionalMedicalEntry("deprywacja")  # 0
        otylosc = self.getOptionalMedicalEntry("otylosc")  # 0
        stres = self.getOptionalMedicalEntry("stres")  # 0
        rodzinne_CVD = self.getOptionalMedicalEntry("rodzinne_CVD")  # 0
        choroba_psychiczna = self.getOptionalMedicalEntry("choroba_psychiczna")  # 0
        HIV = self.getOptionalMedicalEntry("HIV")  # 0
        migotanie_przedsionkow = self.getOptionalMedicalEntry("migotanie_przedsionkow")  # 0
        przerost_lewej_komory = self.getOptionalMedicalEntry("przerost_lewej_komory")  # 0
        bezdech = self.getOptionalMedicalEntry("bezdech")  # 0

        self.addDiagnosisLine('<b>DIAGNOZA LIPIDOWA </b>')

        SCORE = calculate_SCORE(self.patientData.plec, self.patientData.wiek, self.patientData.palenie, self.patientData.cisnienie_skurczowe,
                                self.patientData.cholesterol_calkowity)
        # self.addDiagnosisLine('<br>& wyznaczenie SCORE = {}'.format(SCORE))
        # str. 17/85
        # określenie stopnia ryzyka sercowo-naczyniowego
        # self.addDiagnosisLine('& Ryzyko sercowo-naczyniowe:')
        stopien_ryzyka = ''
        if udokumentowana_CVD or CKD < 30 or SCORE >= 10 \
                or (
                cukrzyca != 0 and (powiklania_narzadowe or palenie or nadcisnienie_tetnicze or zaburzenia_lipidowe)):
            stopien_ryzyka = 'bardzo duże ryzyko'
        elif cholesterol_calkowity > 8 or cukrzyca or 30 <= CKD <= 59 or 5 <= SCORE < 10:
            stopien_ryzyka = 'duże ryzyko'
        elif 1 <= SCORE < 5:
            stopien_ryzyka = 'umiarkowane ryzyko'
        elif SCORE < 1:
            stopien_ryzyka = 'małe ryzyko'
        # self.addDiagnosisLine('- ' + stopien_ryzyka)

        # str. 10/85
        # ile lat ma osoba starsza??
        self.addDiagnosisLine(
            'Łączne ryzyko poważnych incydentów CVD (śmiertelnych + nieprowadzących do zgonu) wynosi{}: {}%'.format(
                ' u osób starszych nieco mniej niż' if self.patientData.wiek > 65 else '', SCORE * 4 if plec else SCORE * 3, ))

        # modyfikacja SCORE przy pomocy HDL-C - gdzie przelicznik?

        # czynniki modyfikujące ryzyko oszacowane za pomocą skali SCORE
        risks = ""
        if deprywacja > 0:
            risks += entryLine('- Deprywacja społeczna — podłoże wielu przyczyn CVD')
        if otylosc > 0:
            risks += entryLine('- Otyłość i otyłość centralna')
        if aktywnosc_fizyczna == 0:
            risks += entryLine('- Brak aktywności fizycznej')
        if stres > 0:
            risks += entryLine('- Stres psychospołeczny, w tym wyczerpanie sił życiowych')
        if rodzinne_CVD > 0:
            risks += entryLine('- Przedwczesna CVD w wywiadach rodzinnych (mężczyźni: < 55 lat; kobiety: < 60 lat)')
        if choroba_autoimmunologiczna > 0:
            risks += entryLine('- Choroby autoimmunologiczne i inne choroby zapalne')
        if choroba_psychiczna > 0:
            risks += entryLine('- Poważne choroby psychiczne')
        if HIV > 0:
            risks += entryLine('- HIV')
        if migotanie_przedsionkow > 0:
            risks += entryLine('- Migotanie przedsionków')
        if przerost_lewej_komory > 0:
            risks += entryLine('- Przerost lewej komory')
        if CKD > 0:  # sprawdzić!!
            risks += entryLine('- Przewlekła choroba nerek')
        if bezdech > 0:
            risks += entryLine('- Zespół obturacyjnego bezdechu sennego')
        if risks != "":
            self.addDiagnosisLine('<br>Występują następujące czynniki modyfikujące ryzyko:')  # str. 15/85
            self.addDiagnosisLine(risks)  # str. 15/85

        # THE BELOW WAS COMMENTED OUT BY Przelaskowski team
        # niedoczynnosc_tarczycy = 0
        # zespol_nerczycowy = 1
        # nadczynnosc_kory_nadnerczy = 0
        # choroby_watroby = 0
        # niedozywienie = 1
        # cukrzyca = 0
        # beta_blokery = 0
        # progestagen = 0
        # kortykosteroidy = 0
        # hipotyreoza = 1
        # zespol_Cushinga = 0
        # leki_immunosupresyjne = 0
        # inhibitory_proteaz_HIV = 0

        # if (niedoczynnosc_tarczycy or zespol_nerczycowy or nadczynnosc_kory_nadnerczy or choroby_watroby or niedozywienie or cukrzyca or beta_blokery or progestagen or kortykosteroidy):
        #     self.addLine('')
        #     self.addLine('U pacjenta występują stany które sprzyjają zaburzeniom lipidowym i ewentualnie trzeba zacząć je leczyć:')
        #     if(niedoczynnosc_tarczycy):
        #         self.addLine('- niedoczynność tarczycy')
        #     if(zespol_nerczycowy):
        #         self.addLine('- zespół nerczycowy')
        #     if(nadczynnosc_kory_nadnerczy):
        #         self.addLine('- nadczynność kory nadnerczy')
        #     if(choroby_watroby):
        #         self.addLine('- choroby wątroby')
        #     if(niedozywienie):
        #         self.addLine('- niedożywienie')
        #     if(cukrzyca):
        #         self.addLine('- zaburzenia gospodarki węglowodanowej (cukrzyca)')
        #     if(beta_blokery):
        #         self.addLine('- przyjmowanie niektórych leków (ß-blokerów)')
        #     if(progestagen):
        #         self.addLine('- przyjmowanie niektórych leków (progestagenów)')
        #     if(kortykosteroidy):
        #         self.addLine('- przyjmowanie niektórych leków (kortykosteroidów)')

        # if (hipotyreoza or cukrzyca or choroby_watroby or zespol_nerczycowy or zespol_Cushinga or kortykosteroidy or leki_immunosupresyjne or inhibitory_proteaz_HIV):
        #     self.addLine('')
        #     self.addLine('Wtórne przyczyny hipercholesterolemii obecne u pacjenta:')
        #     if(hipotyreoza):
        #         self.addLine('- hipotyreoza')
        #     if(cukrzyca):
        #         self.addLine('- cukrzyca')
        #     if(choroby_watroby):
        #         self.addLine('- choroby wątroby')
        #     if (zespol_nerczycowy):
        #         self.addLine('- zespół nerczycowy')
        #     if(zespol_Cushinga):
        #         self.addLine('- zespół Cushinga')
        #     if(kortykosteroidy):
        #         self.addLine('- powodujących wzrost stężenia cholesterolu całkowitego (kortykosteroidów)')
        #     if(leki_immunosupresyjne):
        #         self.addLine('- powodujących wzrost stężenia cholesterolu całkowitego (leków immunosupresyjnych)')
        #     if(inhibitory_proteaz_HIV):
        #         self.addLine('- powodujących wzrost stężenia cholesterolu całkowitego (inhibitorów proteaz HIV)')
        #
        #     self.addLine('W przypadku rozpoznania hipercholesterolemii wtórnej, należy skoncentrować się na leczeniu choroby '
        #           'podstawowej (lekarze różnych specjalności).')

        # hiperlipidemia_wtorna = 0
        # homozygotyczna_postac_hipercholesterolemii_rodzinnej = 0
        # ciezka_niewydolnosc_nerek = 0
        # ciezka_niewydolnosc_watroby = 1
        # ciaza = 0
        # karmienie_piersia = 0
        # nadwrazliwosc_na_alirokumab = 0
        #
        # if (hiperlipidemia_wtorna or homozygotyczna_postac_hipercholesterolemii_rodzinnej or ciezka_niewydolnosc_nerek or
        #         ciezka_niewydolnosc_watroby or ciaza or karmienie_piersia or nadwrazliwosc_na_alirokumab):
        #     self.addLine('')
        #     self.addLine('Warunki wykluczenia:')
        #     if(hiperlipidemia_wtorna):
        #         self.addLine('- hiperlipidemia wtórna')
        #     if(homozygotyczna_postac_hipercholesterolemii_rodzinnej):
        #         self.addLine('- homozygotyczna postać hipercholesterolemii rodzinnej')
        #     if(ciezka_niewydolnosc_nerek):
        #         self.addLine('- ciężka niewydolność nerek')
        #     if(ciezka_niewydolnosc_watroby):
        #         self.addLine('- ciężka niewydolność wątroby')
        #     if(ciaza):
        #         self.addLine('- ciąża')
        #     if(karmienie_piersia):
        #         self.addLine('- karmienie piersią')
        #     if(nadwrazliwosc_na_alirokumab):
        #         self.addLine('- nadwrażliwość na alirokumab lub którąkolwiek z substancji pomocniczych')

        self.addTreatmentLine('')
        self.addTreatmentLine('<b> Aspekt lipidowy - zalecane badania  </b>')
        # ocena lipidogramu
        if (plec == 0 and wiek >= 40) or (plec == 1 and wiek >= 50) or choroba_autoimmunologiczna:
            self.addTreatmentLine('Lipidogram - należy rozważyć badanie laboratoryjne (przesiewowe oznaczanie)')

        self.addTreatmentLine('')
        hipercholesterolemia_rodzinna = 0
        if udokumentowana_CVD or hipercholesterolemia_rodzinna or SCORE >= 5:
            self.addTreatmentLine('Rozważyć przesiewową ocenę stężenia lipoproteiny (a)')

        self.addTreatmentLine('')
        self.addTreatmentLine('Badania: ALT, CK, keratynina/GFR i lipidogram.')

        # leczenie + dawki i rodzaj statyny
        self.addTreatmentLine('')
        self.addTreatmentLine('<b> Aspekt lipidowy - proponowane wskazówki terapii </b>')
        if (LDL_C < 190 and SCORE < 1) or (LDL_C < 100 and 1 <= SCORE < 5) or (
                LDL_C < 70 and (5 <= SCORE < 10 or stopien_ryzyka == 'duże ryzyko')):
            self.addTreatmentLine('Brak interwencji ukierunkowanej na lipidy.')
            if not (LDL_C < 100 and SCORE < 1):
                self.addTreatmentLine('Zalecić zmianę stylu życia.')
        elif (190 <= LDL_C and SCORE < 1) or (100 <= LDL_C and 1 <= SCORE < 5) or (
                70 <= LDL_C < 100 and (5 <= SCORE < 10 or stopien_ryzyka == 'duże ryzyko')) or (
                LDL_C < 70 and (10 <= SCORE or stopien_ryzyka == 'bardzo duże ryzyko')):
            self.addTreatmentLine(
                'Interwencja dotycząca modyfikacji stylu życia, rozważyć farmakoterapię, jeżeli nie uzyskano kontroli.')
            self.addTreatmentLine('Zmiana stylu życia, przy braku efektu rozważyć statynę:', )
            if SCORE < 1 or 155 <= LDL_C < 190:
                self.addTreatmentLine('rosuwastatyna 15mg')
            elif 100 <= LDL_C < 155:
                self.addTreatmentLine('atorwastatyna 40mg')
            elif LDL_C > 190 and 1 <= SCORE < 5:
                self.addTreatmentLine('rosuwastatyna 20mg')
            elif 70 <= LDL_C < 100:
                self.addTreatmentLine('atorwastatyna 30mg')
        elif (100 <= LDL_C and (5 <= SCORE < 10 or stopien_ryzyka == 'duże ryzyko')) or (
                70 <= LDL_C and (10 <= SCORE or stopien_ryzyka == 'bardzo duże ryzyko')):
            self.addTreatmentLine(
                'Interwencja dotycząca modyfikacji stylu życia, rozważyć farmakoterapię, jeżeli nie uzyskano kontroli.')
            self.addTreatmentLine('Zmiana stylu życia i jednoczesna statyna:')
            if (LDL_C > 190 and 5 <= SCORE < 10) or (155 <= LDL_C < 190 and 10 <= SCORE):
                self.addTreatmentLine('rosuwastatyna 30mg')
            elif (100 <= LDL_C < 155 and 10 <= SCORE) or (155 <= LDL_C < 190 and 5 <= SCORE < 10):
                self.addTreatmentLine('rosuwastatyna 20mg')
            elif 190 < LDL_C and 10 <= SCORE:
                self.addTreatmentLine('rosuwastatyna 40mg')
            elif 100 <= LDL_C < 155 and 5 <= SCORE < 10:
                self.addTreatmentLine('rosuwastatyna 15mg')
            elif 70 <= LDL_C < 100 and 10 <= SCORE:
                self.addTreatmentLine('atorwastatyna 60mg')
            elif LDL_C < 70 and 10 <= SCORE:
                self.addTreatmentLine('atorwastatyna 30mg')

        # cele terapeutyczne
        self.addTreatmentLine('<br>Cele terapeutyczne dla pacjenta:')
        if palenie:
            self.addTreatmentLine('\tBrak ekspozycji na tytoń w jakiejkowiek postaci')
        if odzywianie_sie:
            self.addTreatmentLine(
                '\tZdrowa dieta o małej zawartości tłuszczów, z naciskiem na spożycie produktów pełnoziarnistych, warzyw, owoców i ryb')
        if aktywnosc_fizyczna < 2.5:
            self.addTreatmentLine(
                '\tUmiarkowana/intensywna aktywność fizyczna 1,5-5h tygodniowo lub 30-60 min w większość dni.')
        if 20 > BMI or BMI > 25:
            self.addTreatmentLine('\tZmniejszenie/zwiększenie masy ciała.')
        if (obwod_pasa >= 94 and plec == 0) or (obwod_pasa >= 80 and plec == 1):  # wziąć pod uwagę Azjatów
            self.addTreatmentLine('\tZmniejszenie obwód w pasie.')
        if cisnienie_rozkurczowe > 140 or cisnienie_rozkurczowe > 90:
            self.addTreatmentLine('\tObniżenie ciśnienia tętniczego.')
        if LDL_C < 70:
            self.addTreatmentLine(
                '\tPacjent w grupie bardzo dużego ryzyka. Wskazane zmniejszenie o >=50%, jeżeli wartość początkowa wynosi 70-135 mg/dl. Dodatkowy cel terapeutyczny to nie-HDL-C < 100 mg/dl.')
        elif LDL_C < 100:
            self.addTreatmentLine(
                '\tPacjent w grupie dużego ryzyka. Wskazane zmniejszenie o >=50%, jeżeli wartość początkowa wynosi 100-200 mg/dl. Dodatkowy cel terapeutyczny to nie-HDL-C < 130 mg/dl.')
        elif LDL_C < 115:
            self.addTreatmentLine(
                '\tPacjent w grupie małego lub umiarkowanego ryzyka. Dodatkowy cel terapeutyczny dla umiarkowanego ryzyka to nie-HDL-C < 145 mg/dl.')
        if cukrzyca_HbA >= 53:
            self.addTreatmentLine('\tStężenie HbA < 7% (< 53 mmol/mol)')

        # wykluczenie innych przyczyn zaburzeń lipidowych

    def addDiagnosisLine(self, line):
        self.payload.diagnosis.manualDiagnosis += line + "<br>"

    def addTreatmentLine(self, line):
        self.payload.treatment_plan += line + "<br>"


def entryLine(line):
    return line + "<br>"
