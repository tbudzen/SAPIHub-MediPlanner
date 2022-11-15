class CHA2DS2_VASc(object):

    def __init__(self, payload, patientData) -> None:
        self.patientData = patientData
        self.payload = payload

    def calculateFromPatientData(self):
        dysfunkcja_lewej_komory = -1
        nadcisnienie_tetnicze = -1
        if self.patientData.nadcis_przer_lkomory == 1:
            dysfunkcja_lewej_komory = 1
        if self.patientData.przerost_lewej_komory == 1:
            dysfunkcja_lewej_komory = 1
        if self.patientData.klasa_nadcisn >= 5:
            nadcisnienie_tetnicze = 1

        return self.calculate(self.patientData.niewydolnosc_serca, dysfunkcja_lewej_komory, nadcisnienie_tetnicze, self.patientData.wiek, self.patientData.cukrzyca, self.patientData.udar,
                              self.patientData.incydent_zakrzep_zator, self.patientData.choroba_naczyniowa, self.patientData.plec)

    def calculate(self, zastoinowa_niewydolnosc_serca, dysfunkcja_lewej_komory, nadcisnienie_tetnicze, wiek, cukrzyca, udar_mozgu, incydent_zakrzep_zator, choroba_naczyniowa, plec):
        # choroba naczyniowa (przebyty zawał serca, miażdżycowa choroba tętnic obwodowych, blaszki miażdżycowe w aorcie)
        score = 0
        source = []
        if zastoinowa_niewydolnosc_serca > 0 or dysfunkcja_lewej_komory > 0:
            score += 1
            source.append("zastoinowa niewydolność serca/dysfunkcja lewej komory, score +1 ")
        if nadcisnienie_tetnicze > 0:
            score += 1
            source.append("nadciśnienie tętnicze, score +1 ")
        if wiek >= 75:
            score += 1
            source.append("wiek >= 75, score +1 ")
        if wiek >= 65:
            score += 1
            source.append("wiek >= 65, score +1 ")
        if cukrzyca > 0:
            score += 1
            source.append("cukrzyca, score +1 ")
        if udar_mozgu > 0 or incydent_zakrzep_zator > 0:
            score += 1
            source.append("przebyty udar mózgu/TIA/incydent zakrzepowo-zatorowy, score +1 ")
        if choroba_naczyniowa > 0:
            score += 1
        source.append("choroba naczyniowa (przebyty zawał serca, miażdżycowa choroba tętnic obwodowych, blaszki miażdżycowe w aorcie)		, score +1 ")
        if plec == 1:
            score += 1
            source.append("płeć żeńska, score +1 ")
        return score, source

    def getText(self, score, plec):
        if ((score == 0 and plec == 0) or (score == 1 and plec == 1)):
            return {"ryzyko": "niskie", "Leczenie_przeciwzakrzepowe": "Nie zaleca się", "leki": "Brak leczenia"}
        if ((score == 1 and plec == 0)):
            return {"ryzyko": "Umiarkowane",
                    "Leczenie_przeciwzakrzepowe": "Można rozważyć",
                    "leki": "Rozważyć opcje: <br>\t\t1. Brak leczenia"
                            " <br>\t\t2. Doustny antykoagulant starego typu (tzw VKA) np. acenokumarol (Sintrom), warfaryna (Warfin). Należy wówczas utrzymywać krzepliwość krwi (INR) w zakresie 2-3 wykonując pomiary średnio raz w miesiącu tak aby krew była odpowiednio rozrzedzona przez co najmniej 60-70% całego okresu leczenia."
                            " <br>\t\t3. Doustny antykoagulant nowego typu (tzw NOAC) np dabigatran (Pradaxa), rivaroksaban (Xarelto), apixaban (Eliquis). Krew na tych lekach jest odpowiednio rozrzedzona i nie trzeba robić badań kontrolnych."
                            "<br>\t\t4. Wyjątkowo (ze względów logistyczno - finansowych) zamiast powyższych leków można rozważyć znacznie mniej skuteczny kwas acetylosalicylowy (Aspiryna, Acard, Polocard)."}
        if ((score >= 2)):
            return {"ryzyko": "Wysokie",
                    "Leczenie_przeciwzakrzepowe": "Należy zastosować doustny antykoagulant",
                    "leki": "Rozważyć opcje: <br>\t\t1. Doustny antykoagulant starego typu (tzw VKA) np acenokumarol (Sintrom), warfaryna (Warfin). Należy wówczas utrzymywać krzepliwość krwi (INR) w zakresie 2-3 wykonując pomiary średnio raz w miesiącu tak aby krew była odpowiednio rozrzedzona przez co najmniej 60-70% całego okresu leczenia."
                            "<br>\t\t2. Doustny antykoagulant nowego typu (tzw NOAC) np dabigatran (Pradaxa), rivaroksaban (Xarelto), apixaban (Eliquis). Krew na tych lekach jest odpowiednio rozrzedzona i nie trzeba robić badań kontrolnych."

                            "<br>\t\t3. Wyjątkowo (ze względów logistyczno - finansowych) zamiast powyższych leków można rozważyć znacznie mniej skuteczny kwas acetylosalicylowy (Aspiryna, Acard, Polocard)."}
