class HypertensionTreatmentPlan(object):

    def __init__(self, payload, patientData) -> None:
        self.patientData = patientData
        self.payload = payload

    def generateTreatmentPlan(self):
        self.addLine('<b>Terapia NT - rozpoczęcie terapii w nadciśnieniu tętniczymi i cele leczenia, schematy leczenia</b>')
        self.addLine('<i>progi, zlecenia i cele</i>')
        if self.patientData.cisnienie_rozkurczowe >= 90:
            self.addLine('Rozpocząć terapię dla ciśnienia rozkurczowego - cel: obniżenie do poziomu 70-79 mmHg')
        if self.patientData.klasa_nadcisn == 4:
            self.addLine('Porada dot. zmian stylu życia.')
            if (self.patientData.ryzyko == 3) and (
                    self.patientData.CAD > 0 or self.patientData.rewaskularyzacja_wiencowa_lub_inna > 0 or self.patientData.choroba_tetnic_obwodowych > 0 or self.patientData.tetniak_aorty > 0):
                self.addLine('Rozważyć leczenie u pacentów z cisnieniem wysokim prawidłowym ')
        if self.patientData.klasa_nadcisn >= 5:
            if self.patientData.cukrzyca > 0 or self.patientData.CKD > 0:
                if self.patientData.cisnienie_skurczowe >= 140 and 18 <= self.patientData.wiek < 65:
                    if self.patientData.cukrzyca > 0:
                        self.addLine(
                            'Rozpocząć terapię dla ciśnienia skurczowego - cel: obniżenie do poziomu 120-130 mmHg')
                    else:
                        self.addLine(
                            'Rozpocząć terapię dla ciśnienia skurczowego - cel: obniżenie do poziomu 139-130 mmHg')
                elif self.patientData.cisnienie_skurczowe >= 140 and 65 <= self.patientData.wiek < 80:
                    self.addLine(
                        'Rozpocząć terapię dla ciśnienia skurczowego - cel: obniżenie do poziomu 130-139 mmHg')
            elif self.patientData.cisnienie_skurczowe >= 160 and self.patientData.wiek >= 80:
                self.addLine('Rozpocząć terapię dla ciśnienia skurczowego - cel: obniżenie do poziomu 130-139 mmHg')
        elif self.patientData.CAD > 0 or self.patientData.udar > 0:
            if (self.patientData.cisnienie_skurczowe >= 140 or (
                    self.patientData.cisnienie_skurczowe >= 130 and self.patientData.ryzyko == 3)) and 18 <= self.patientData.wiek < 65:
                self.addLine('Rozpocząć terapię dla ciśnienia skurczowego - cel: obniżenie do poziomu 120-130 mmHg')
            elif (self.patientData.cisnienie_skurczowe >= 140 or (
                    self.patientData.cisnienie_skurczowe >= 130 and self.patientData.ryzyko == 3)) and 65 <= self.patientData.wiek < 80:
                self.addLine('Rozpocząć terapię dla ciśnienia skurczowego - cel: obniżenie do poziomu 130-139 mmHg')
            elif self.patientData.cisnienie_skurczowe >= 160 and self.patientData.wiek >= 80:
                self.addLine('Rozpocząć terapię dla ciśnienia skurczowego - cel: obniżenie do poziomu 130-139 mmHg')
        if self.patientData.klasa_nadcisn == 5:
            self.addLine('Porada dot. zmian stylu życia.')
            if (
                    self.patientData.CVD > 0 and self.patientData.ryzyko >= 2) or self.patientData.choroba_nerek > 0 or self.patientData.HMOD > 0:  # or powiklania_narzadowe >0
                self.addLine(
                    'Natychmiast rozpocznij farmakoterapię u pacjentów z CVD z wysokim i bardzo wysokim ryzykiem, chorobą nerek czy HMOD.')
            else:
                self.addLine(
                    'Farmakoterapia, gdy po 3-6 miesiącach od interwencji dot. zmian stylu życia BP jest źle kontrolowane.')

        elif self.patientData.klasa_nadcisn == 6 or self.patientData.klasa_nadcisn == 7:
            self.addLine('Porada dot. zmian stylu życia.')
            self.addLine('Rozpocząć farmakoterapię natychmiast, by osiągnąć cel w ciągu 3 miesięcy')
        # metody leczenia
        self.addLine('')
        if self.patientData.klasa_nadcisn <= 4:
            pass
        elif self.patientData.migotanie_przedsionkow > 0:
            self.addLine('Terapia początkowa - skojarzenie dwóch leków:<br>'
                         '\ta) inhibitor ACE lub ARB + \u03B2-adrenolityk<br>'
                         '\tb) nie-DHP CCB lub \u03B2-andrenolityk + CCB<br>'
                         'Krok 2 - skojarzenie trzech leków:<br>'
                         '\ta) inhibitor ACE lub ARB + \u03B2-adrenolityk + DHP CCB lub diuretyk<br>'
                         '\tb) \u03B2-andrenolityk + DHP CCB + diuretyk')
            self.addLine(
                'Należy włączyć leki przeciwkrzepliwe, jeśli wynik w skali CHA₂DS₂-VASc wskazuje na taką konieczność, przy braku przeciwskazań.')
        elif self.patientData.HFrEF > 0:
            self.addLine(
                'Terapia początkowa:<br>\tinhibitor ACE lub ARB + diuretyk (lub diuretyk pętlowy) + \u03B2-adrenolityk<br>'
                'Krok 2:<br>\tinhibitor ACE lub ARB + diuretyk (lub diuretyk pętlowy) + \u03B2-adrenolityk + MRA')
            self.addLine(
                'Jeśli u pacjentów z HFrEF nie jest konieczna terapia przeciwnadciśnieniowa, należy prowadzić leczenie zgodnie '
                'z wytycznymi ESC dot. postępowania w niewydolności serca.')
        elif self.patientData.CKD > 0:
            self.addLine('Terapia początkowa - lek dwuskładnikowy:<br>'
                         '\ta) inhibitor ACE lub ARB + CCB<br>'
                         '\tb) inhibitor ACE lub ARB + diuretyk (lub diuretyk pętlowy)')
            self.addLine(
                'Krok 2 - lek trójskładnikowy:<br>\tinhibitor ACE lub ARB + CCB + diuretyk (lub diuretyk pętlowy).')
            self.addLine(
                'Krok 3 - lek trójskładnikowy + spironolakton lub inny lek:<br>\toporne nadciśnienie tętnicze<br>'
                '\tDodaj spironolakton (25-50mg o.d.) lub inny diuretyk \u03B1-adrenolityk lub \u03B2-adrenolityk')
            self.addLine(
                'Rozważ stosowanie \u03B2-adrenolityków na każdym etapie leczenia, w sytuacji występowanie jednoznacznych '
                'wskazań do ich podawania, takich jak niewydolność serca, dławica piersiowa, stan po MI, migotanie przedsionków, '
                'lub u młodszych pacjentek w ciąży lub planujących ciążę.')
        elif self.patientData.choroba_wiencowa > 0:
            self.addLine('Terapia początkowa - lek dwuskładnikowy:<br>'
                         '\ta) inhibitor ACE lub ARB + \u03B2-adrenolityk lub CCB<br>'
                         '\tb) CCB + diuretyk lub \u03B2-adrenolityk<br>'
                         '\tc) \u03B2-adrenolityk + diuretyk')
            if self.patientData.klasa_nadcisn == 5 or self.patientData.wiek >= 80 or self.patientData.zespol_kruchosci > 0:
                self.addLine('\tRozważ monoterapię.')
            self.addLine('Krok 2 - lek trójskładnikowy:<br>\tTerapia złożona z 3 leków wymienionych powyżej.')
            if self.patientData.CVD > 0 or self.patientData.ryzyko == 3:
                self.addLine('\tRozważ rozpoczęcie terapii od tego etapu.')
            self.addLine(
                'Krok 3 - lek trójskładnikowy + spironolakton lub inny lek:<br>\toporne nadciśnienie tętnicze<br>'
                '\tDodaj spironolakton (25-50mg o.d.) lub inny diuretyk \u03B1-adrenolityk lub \u03B2-adrenolityk<br>'
                '\tRozważ skierowanie do ośrodka specjalistycznego w celu wykonania dalszych badań.')
        else:
            self.addLine('Terapia początkowa - lek dwuskładnikowy:<br>\tinhibitor ACE lub ARB + CCB lub diuretyk<br>'
                         'Krok 2 - lek trójskładnikowy:<br>\tinhibitor ACE lub ARB + CCB + diuretyk<br>'
                         'Krok 3 - lek trójskładnikowy + spironolakton lub inny lek:<br>\toporne nadciśnienie tętnicze<br>'
                         '\tDodaj spironolakton (25-50mg o.d.) lub inny diuretyk \u03B1-adrenolityk lub \u03B2-adrenolityk')
            self.addLine(
                'Rozważ stosowanie \u03B2-adrenolityków na każdym etapie leczenia, w sytuacji występowanie jednoznacznych '
                'wskazań do ich podawania, takich jak niewydolność serca, dławica piersiowa, stan po MI, migotanie przedsionków, '
                'lub u młodszych pacjentek w ciąży lub planujących ciążę.')

    def generateContraindications(self):

        # przeciwskazania str. 40/89

        avoid=""
        if self.patientData.dna_moczanowa > 0:
          avoid+=(' - Diuretyki - bewzględne przeciwskazanie')
        elif self.patientData.zespol_metaboliczny > 0 or self.patientData.nietolerancja_glukozy > 0 or self.patientData.ciaza > 0 or self.patientData.hiperkalcemia > 0 or self.patientData.hipokaliemia > 0:
          avoid+=(' - Diuretyki - względne przeciwskazanie')
        if self.patientData.astma > 0 or self.patientData.blok_przedsionkowo_komorowy > 0 or self.patientData.blok_zatokowo_przedsionkowy > 0:
          avoid+=(' - Beta-adrenolityki - bezwzględne przeciwskazanie')
        elif self.patientData.zespol_metaboliczny > 0 or self.patientData.nietolerancja_glukozy > 0 or self.patientData.aktywnosc_fizyczna > 2.5:
          avoid+=(' - Beta-adrenolityki - względne przeciwskazanie')
        if self.patientData.tachyarytmia > 0 or self.patientData.niewydolnosc_serca > 0 or self.patientData.obrzek_konczyn_dolnych > 0:
          avoid+=(' - Antagoniści wapnia (pochodne dihydropirydynowe) - względne przeciwskazanie')
        if self.patientData.blok_zatokowo_przedsionkowy > 0 or self.patientData.blok_przedsionkowo_komorowy > 0 or self.patientData.dysfunkcja_LV > 0 or self.patientData.bradykardia > 0:
          avoid+=(' - Antagoniści wapnia (werapamil, diltiazem) - bezwzględne przeciwskazanie')
        elif self.patientData.zaparcia > 0:
          avoid+=(' - Antagoniści wapnia (werapamil, diltiazem) - względne przeciwskazanie')
        if self.patientData.ciaza > 0 or self.patientData.obrzek_naczynioruchowy > 0 or self.patientData.hiperkaliemia > 0 or self.patientData.obustronne_zwezenie_tetnic_nerkowych > 0:
          avoid+=(' - Inhibitory ACE - bewzględne przeciwskazanie')
        elif self.patientData.wiek < 45 and self.patientData.stosowanie_srodkow_antykoncepcyjnych < 1:
          avoid+=(' - Inhibitory ACE - względne przeciwskazanie')
        if self.patientData.ciaza > 0 or self.patientData.hiperkaliemia > 0 or self.patientData.obustronne_zwezenie_tetnic_nerkowych > 0:
          avoid+=(' - ARB - bewzględne przeciwskazanie')
        elif self.patientData.wiek < 45 and self.patientData.stosowanie_srodkow_antykoncepcyjnych < 1:
          avoid+=(' - ARB - względne przeciwskazanie')

        if avoid!="":
         self.addLine('<b>Przeciwskazania:</b>')
         self.addLine(avoid)

    def addLine(self, line):
        self.payload.treatment_plan += line + "<br>"
