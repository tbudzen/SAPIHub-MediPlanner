class HypertensionMissingDataTexts():

    def __init__(self, hyperTensionClassifier) -> None:
        self.missingDataAdditionalText =""


    def markMissing(self, patientData, CKD, CVD, EKG, HDL_C, LDL_C, akromegalia, aktywnosc_fizyczna, alkohol, badanie_dna_oka,
                    badanie_moczu, badanie_neurologiczne, badanie_palpacyjne, badanie_palpacyjne_nerek,
                    badanie_palpacyjne_tetnic_obwodowych, bezdech, bmi, choroba_nerek, ciaza, dieta, glikemia,
                    hematokryt, hemoglobina, hemoglobina_glikowana, hipercholesterolemia, hipokaliemia, incydenty,
                    klasa_nadcisn, kreatynina, kwas_moczowy, nadcisnienie_tetnicze_rodzinne, nadcisnienie_w_ciazy,
                    nagly_rozwoj_nadcisnienia, narkotyki, obwod_talii, osluchanie_serca, osluchanie_tetnic_nerkowych,
                    osluchanie_tetnic_szyjnych, palenie, parametry_funkcji_watroby, patologie_kardiologiczne,
                    patologie_nerkowe, patologie_tetnic_obwodowych, porownanie_BP_na_obu_ramionach, porownanie_tetna,
                    potas, rodzinne_CVD, sod, stan_przedrzucawkowy, tarczyca, triglicerydy, udar, uklad_moczowy,
                    wczesne_nadcisnienie, wyglad_skory, zaburzenia_erekcji,
                    zaburzenia_lub_bol_glowy_oczu_patologie_mozgu, zaburzenia_snu, zespol_Cushinga):
        self.patientData = patientData
        self.addTextOfMissing('')
        self.addTextOfMissing(
            'Najważniejsze informacje z wywiadu i wywiadu rodzinnego, które należy uzyskać jeszcze od pacjenta:')
        # Kategoria ryzyka
        if nadcisnienie_tetnicze_rodzinne == -1 or klasa_nadcisn == -1:
            self.addTextOfMissing(' - Wywiad osobisty i rodzinny w kierunku nadciśnienia tętniczego')
        if rodzinne_CVD == -1:
            self.addTextOfMissing(' - Wywiad rodzinny w kierunku CVD')
        if CVD == -1:
            self.addTextOfMissing(' - Wywiad osobisty w kierunku CVD')
        if udar == -1:
            self.addTextOfMissing(' - Wywiad osobisty i rodzinny w kierunku udaru')
        if choroba_nerek == -1:
            self.addTextOfMissing(' - Wywiad osobisty i rodzinny w kierunku choroby nerek')
        if hipercholesterolemia == -1:
            self.addTextOfMissing(' - Wywiad osobisty i rodzinny dotyczący czynników ryzyka (np. rodzinna hipercholesterolemia)')
        if palenie == -1:
            self.addTextOfMissing(' - Wywiad w kierunku palenia tytoniu')
        if dieta == -1:
            self.addTextOfMissing(' - Stosowana dieta i spożycie soli')
        if alkohol == -1:
            self.addTextOfMissing(' - Ilość spożywanego alkoholu')
        if aktywnosc_fizyczna == -1:
            self.addTextOfMissing(' - Brak wysiłku fizycznego/siedzący tryb życia')
        if zaburzenia_erekcji == -1:
            self.addTextOfMissing(' - Zaburzenia erekcji')
        if zaburzenia_snu == -1:
            self.addTextOfMissing(
                ' - Wywiad w kierunku zaburzeń snu, chrapanie, nykturia, bezdech senny (także informacje od partnera)')
        if nadcisnienie_w_ciazy == -1 or stan_przedrzucawkowy == -1:
            self.addTextOfMissing(' - Przebyte nadciśnienie tętnicze związane z ciążą/stan przedrzucawkowy')
        # Wywiad i objawy HMOD, CVD, udaru i choroby nerek
        if zaburzenia_lub_bol_glowy_oczu_patologie_mozgu == -1:
            self.addTextOfMissing(
                ' - Mózg i patologie_kardiologiczne: bóle głowy, zawroty głowy, omdlenia, zaburzenia widzenia, TIA,'
                ' ubytki czuciowe lub ruchowe, udar, rewaskularyzacja tętnic szyjnych, upośledzenie funkcji poznawczych, otępienie (u osób starszych)')
        if patologie_kardiologiczne == -1:
            self.addTextOfMissing(
                ' - Serce: ból w klatce piersiowej, duszność, obrzęki, zawał serca, rewaskularyzacja wieńcowa, omdlenia, kołatania serca w wywiadzie, zaburzenia rytmu serca (szczególnie AF), niewydolność serca')
        if patologie_nerkowe == -1:
            self.addTextOfMissing(' - Nerki: pragnienie, poliuria, nykturia, krwiomocz, infekcje układu moczowego')
        if patologie_tetnic_obwodowych == -1:
            self.addTextOfMissing(
                ' - Tętnice obwodowe: zimne kończyny, chromanie przestankowe, dystans chromania, ból w spoczynku, rewaskularyzacja naczyń obwodowych')
        if CKD == -1:
            self.addTextOfMissing(' - Wywiad osobisty i rodzinny w kierunku CKD (np. wielotorbielowatość nerek)')
        # Wywiad w kierunku możliwych wtórnych przyczyn nadciśnienia
        if wczesne_nadcisnienie == -1 or nagly_rozwoj_nadcisnienia == -1:
            self.addTextOfMissing(
                ' - Wczesne pojawienie się nadciśnienia tętniczego 2.–3. stopnia (< 40. rż.) lub nagły rozwój nadciśnienia bądź szybkie pogorszenie się kontroli BP u osób starszych')
        if choroba_nerek == -1 or uklad_moczowy == -1:
            self.addTextOfMissing(' - Wywiad w kierunku chorób nerek, zakażeń układu moczowego')
        if narkotyki == -1:
            self.addTextOfMissing(
                ' - Zażywanie narkotyków lub innych substancji uzależniających/inne zażywane leki: kortykosteroidy, leki obkurczające śluzówkę nosa, chemioterapia, johimbina, lukrecja')
        if incydenty == -1:
            self.addTextOfMissing(
                ' - Powtarzające się incydenty potliwości, bólów głowy, niepokoju lub kołatań serca, sugerujące guz chromochłonny')
        if hipokaliemia == -1:
            self.addTextOfMissing(
                ' - Wywiad w kierunku samoistnej lub prowokowanej diuretykami hipokaliemii, epizody osłabienia oraz skurczów mięśniowych (hiperaldosteronizm)')
        if tarczyca == -1:
            self.addTextOfMissing(' - Objawy sugerujące chorobę tarczycy lub nadczynność przytarczyc')
        if ciaza == -1:
            self.addTextOfMissing(
                ' - Wywiad w kierunku przebiegu dotychczasowych ciąż lub aktualnej ciąży lub stosowania środków antykoncepcyjnych')
        if bezdech == -1:
            self.addTextOfMissing(' - Wywiad sugerujący bezdech senny')
        tolerancja_lekow = -1
        przestrzeganie_zalecen = 1
        # Leczenie przeciwnadciśnieniowe
        if tolerancja_lekow == -1:
            self.addTextOfMissing(
                ' - Obecne/dawne leczenie przeciwnadciśnieniowe, w tym skuteczność i tolerancja poprzednio stosowanych leków')
        if przestrzeganie_zalecen == -1:
            self.addTextOfMissing(' - Przestrzeganie zaleceń lekarskich')
        self.addTextOfMissing('')
        self.addTextOfMissing('Główne elementy badania przedmiotowego, których brakuje:')
        # Budowa ciała
        if bmi == -1:
            self.addTextOfMissing(' - Ciężar ciała i wzrost zmierzone za pomocą skalibrowanego urządzenia,z obliczeniem BMI')
        if obwod_talii == -1:
            self.addTextOfMissing(' - Obwód talii')
        # Cechy HMOD
        if badanie_neurologiczne == -1:
            self.addTextOfMissing(' - Badanie neurologiczne i ocena funkcji poznawczych')
        if badanie_dna_oka == -1:
            self.addTextOfMissing(' - Badanie dna oka w kierunku retinopatii nadciśnieniowej')
        if badanie_palpacyjne == -1 or osluchanie_serca == -1 or osluchanie_tetnic_szyjnych == -1:
            self.addTextOfMissing(' - Badanie palpacyjne i osłuchiwanie serca i tętnic szyjnych')
        if badanie_palpacyjne_tetnic_obwodowych == -1:
            self.addTextOfMissing(' - Badanie palpacyjne tętnic obwodowych')
        if porownanie_BP_na_obu_ramionach == -1:
            self.addTextOfMissing(' - Porównanie wartości BP na obu ramionach (co najmniej jeden raz)')
        # Wtórne nadciśnienie tętnicze
        if wyglad_skory == -1:
            self.addTextOfMissing(' - Ocena wyglądu skóry: plamy cafe-au-lait w nerwiakowłókniakowatości (guz chromochłonny)')
        if badanie_palpacyjne_nerek == -1:
            self.addTextOfMissing(' - Badanie palpacyjne nerek w kierunku powiększenia w wielotorbielowatości nerek')
        if osluchanie_serca == -1 or osluchanie_tetnic_nerkowych == -1:
            self.addTextOfMissing(
                ' - Osłuchiwanie serca i tętnic nerkowych w kierunku szmerów wskazujących na koarktację aorty lub nadciśnienie naczyniowo-nerkowe')
        if porownanie_tetna == -1:
            self.addTextOfMissing(
                ' - Porównanie tętna na tętnicach promieniowej i udowej — w poszukiwaniu promieniowo-udowego opóźnienia fali tętna w koarktacji aorty')
        if zespol_Cushinga == -1 or akromegalia:
            self.addTextOfMissing(' - Cechy zespołu Cushinga i objawy akromegalii')
        if tarczyca == -1:
            self.addTextOfMissing(' - Objawy chorób tarczycy')
        self.addTextOfMissing('')
        self.addTextOfMissing('Brak poniższych rutynowych badań laboratoryjnych:')
        if hemoglobina == -1 or hematokryt == -1:
            self.addTextOfMissing(' - Hemoglobina i/lub hematokryt')
        if glikemia == -1 or hemoglobina_glikowana == -1:
            self.addTextOfMissing(' - Glikemia na czczo i hemoglobina glikowana (HbA1c)')
        if self.patientData.cholesterol_calkowity == -1 or LDL_C == -1 or HDL_C == -1:
            self.addTextOfMissing(' - Profil lipidowy: cholesterol całkowity, LDL-C, HDL-C')
        if triglicerydy == -1:
            self.addTextOfMissing(' - Triglicerydy')
        if sod == -1 or potas == -1:
            self.addTextOfMissing(' - Sód i potas w surowicy')
        if kwas_moczowy == -1:
            self.addTextOfMissing(' - Kwas moczowy')
        if kreatynina == -1 or self.patientData.eGFR == -1:
            self.addTextOfMissing(' - Kreatynina i eGFR')
        if parametry_funkcji_watroby == -1:
            self.addTextOfMissing(' - Parametry funkcji wątroby')
        if badanie_moczu == -1:
            self.addTextOfMissing(
                ' - Badanie moczu: badanie mikroskopowe osadu, białkomocz: test paskowy lub, najlepiej, wskaźnik albumina–kreatynina')
        if EKG == -1:
            self.addTextOfMissing(' - 12-odprowadzeniowy EKG')


    def addTextOfMissing(self, line):
        self.missingDataAdditionalText +=line


