class RedundantVars(object):

    def __init__(self, payload) -> None:
        self.patientData = {}
        self.payload = payload

    def classify(self):
        nadcisnienie_tetnicze_rodzinne = self.getData("nadcisnienie_tetnicze_rodzinne")

        hipercholesterolemia = self.getData("hipercholesterolemia")
        dieta = self.getData("dieta")
        alkohol = self.getData("alkohol")
        zaburzenia_erekcji = self.getData("Zaburzenia erekcji")
        zaburzenia_snu = self.getData("zaburzenia_snu")
        nadcisnienie_w_ciazy = self.getData("nadcisnienie_w_ciazy")
        stan_przedrzucawkowy = self.getData("stan_przedrzucawkowy")

        HBPM = self.getData("HBPM")  # 0

        zaburzenia_lub_bol_glowy_oczu_patologie_mozgu = self.getData(
            "zaburzenia_lub_ból_głowy_oczu_patologie_mózgu")  # 0
        patologie_kardiologiczne = self.getData("patologie_kardiologiczne")  # 1

        # serce = self.getData("serce") # -1
        patologie_nerkowe = self.getData("patologie_nerkowe")  # 0
        patologie_tetnic_obwodowych = self.getData("patologie_tetnic_obwodowych")  # 1

        # below were never used!!!!
        # wczesne_nadcisnienie = 0
        # nagly_rozwoj_nadcisnienia = 0
        # uklad_moczowy = 0
        # narkotyki = 1
        # incydenty = 0
        # tarczyca = -1
        # hipokaliemia = 0

        wzrost = 1.60
        waga = 60

        # below were never used!!!!
        #        bmi = waga / (wzrost ** 2)

        #below were never used!!!!
        # obwod_talii = -1
        # badanie_neurologiczne = 0
        # badanie_dna_oka = -1
        # badanie_palpacyjne = 0
        # osluchanie_serca = 1
        # osluchanie_tetnic_szyjnych = 1
        # badanie_palpacyjne_tetnic_obwodowych = 1
        # porownanie_BP_na_obu_ramionach = 1
        # wyglad_skory = 0
        # badanie_palpacyjne_nerek = 0
        # osluchanie_tetnic_nerkowych = 0
        # porownanie_tetna = 0
        # zespol_Cushinga = -1
        # akromegalia = -1
        #
        # hemoglobina = -1
        # hematokryt = -1
        # glikemia = 0
        # hemoglobina_glikowana = 0
        # LDL_C = 0
        # HDL_C = 0
        # triglicerydy = 0
        # sod = 0
        # potas = 0
        # kwas_moczowy = 0
        # kreatynina = 0
        # parametry_funkcji_watroby = 0
        # badanie_moczu = 0
        # EKG = 0


        #start missing data code - most of the vars are not used by the Przelaskowski prof code....
        # HypertensionMissingDataTexts(self).markMissing(self.patientData, CKD, CVD, EKG, HDL_C, LDL_C, akromegalia, aktywnosc_fizyczna, alkohol, badanie_dna_oka,
        #                  badanie_moczu, badanie_neurologiczne, badanie_palpacyjne, badanie_palpacyjne_nerek,
        #                  badanie_palpacyjne_tetnic_obwodowych, bezdech, bmi, choroba_nerek, ciaza, dieta, glikemia,
        #                  hematokryt, hemoglobina, hemoglobina_glikowana, hipercholesterolemia, hipokaliemia, incydenty,
        #                  klasa_nadcisn, kreatynina, kwas_moczowy, nadcisnienie_tetnicze_rodzinne, nadcisnienie_w_ciazy,
        #                  nagly_rozwoj_nadcisnienia, narkotyki, obwod_talii, osluchanie_serca,
        #                  osluchanie_tetnic_nerkowych, osluchanie_tetnic_szyjnych, palenie, parametry_funkcji_watroby,
        #                  patologie_kardiologiczne, patologie_nerkowe, patologie_tetnic_obwodowych,
        #                  porownanie_BP_na_obu_ramionach, porownanie_tetna, potas, rodzinne_CVD, sod,
        #                  stan_przedrzucawkowy, tarczyca, triglicerydy, udar, uklad_moczowy, wczesne_nadcisnienie,
        #                  wyglad_skory, zaburzenia_erekcji, zaburzenia_lub_bol_glowy_oczu_patologie_mozgu,
        #                  zaburzenia_snu, zespol_Cushinga)

        #end missing