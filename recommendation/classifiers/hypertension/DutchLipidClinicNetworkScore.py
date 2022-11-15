# http://hipercholesterolemia.com.pl/Kryteria_kliniczne,8,56.html
# https://docs.google.com/document/d/1ZmHmr6CDJMU5bTAuFiVVxAnPSx_AY9Aw1r1wtukjXrY/edit
from recommendation.processStep.ExtractDataFromText import ExtractAdditionalDataFromText


class DutchLipidClinicNetworkScore(object):

    def __init__(self, payload, patientData) -> None:
        self.patientData = patientData
        self.payload = payload
        self.dataFromText = ExtractAdditionalDataFromText(payload, patientData)

    def calculateFromPatientData(self):

        score = 0
        source = []
        wiek = self.patientData.wiek
        choroba_wiencowa = self.patientData.choroba_wiencowa
        plec = self.patientData.plec
        dataFromText = self.dataFromText
        if (choroba_wiencowa > 0) and (wiek < 55 and plec == 0 or wiek < 60 and plec == 1):
            score += 2
            source.append("Przedwczesna choroba wieńcowa (mężczyźni < 55 rż., kobiety < 60 rż.), score +2 ")
        if (dataFromText.checkAdHocText("choroba naczyń mózgowych") > 0 or dataFromText.checkAdHocText("choroba naczyń obwodowych") > 0) and (wiek < 55 and plec == 0 or wiek < 60 and plec == 1):
            score += 1
            source.append("Przedwczesna choroba naczyń mózgowych lub obwodowych, score +1 ")
        if (dataFromText.checkAdHocTextR("(?:Krewni|Rodzina)przedwczesn. chorob. wie.cow. lub naczyniow.", "Krewni I stopnia z przedwczesną chorobą wieńcową lub naczyniową") > 0):
            score += 1
            source.append("Krewni I stopnia z przedwczesną chorobą wieńcową lub naczyniową, score +1 ")
        if (dataFromText.checkAdHocTextR("(?:Krewni|Rodzina).{0,100}LDL[ ]{0,2}\>[ ]{0,2}190[ ]{0,2}mg.dl", "Krewni I stopnia ze stężeniem cholesterolu LDL > 190 mg/dl") > 0):
            score += 1
            source.append("Krewni I stopnia ze stężeniem cholesterolu LDL > 190 mg/dl, score +1 ")

        if (dataFromText.checkAdHocTextR("(?:Krewni|Rodzina).{0,100}(?:żółtak.{0,100} ścięgien|rąb.{0,20} rogówk)", "Krewni I stopnia z żółtakami ścięgien i/lub rąbkiem rogówkowym") > 0):
            score += 2
            source.append("Krewni I stopnia z żółtakami ścięgien i/lub rąbkiem rogówkowym, score +2 ")

        if (wiek < 18 and self.patientData.LDL_C > 155):
            score += 2
            source.append(" Dzieci i młodzież < 18 rż. ze stężeniem cholesterolu LDL > 155 mg/dl, score +2 ")

        # negative regex lookup for family
        if (dataFromText.checkAdHocTextR("^(?!.*Krewni).*[Żż]ółtaki ścięgien.*$", "Żółtaki ścięgien") > 0):
            score += 6
            source.append("Żółtaki ścięgien, score +6 ")

        # negative regex lookup for family
        if (wiek < 45 and dataFromText.checkAdHocTextR("^(?!.*Krewni).*[rR]ąbek rogówkowy.*$", "Rąbek rogówkowy") > 0):
            score += 4
            source.append("Rąbek rogówkowy < 45rż, score +4 ")

        if (self.patientData.LDL_C >= 330):
            score += 8
            source.append(" Cholesterol LDL >= 8,5 mmol/l (330 mg/dl) , score +8 ")

        elif (self.patientData.LDL_C >= 250):
            score += 5
            source.append(" Cholesterol LDL 6,5-8,4 mmol/l (250-329 mg/dl) , score +5 ")

        elif (self.patientData.LDL_C >= 198):
            score += 3
            source.append(" Cholesterol LDL 5,0-6,4 mmol/l (190-249 mg/dl), score +3")

        elif (self.patientData.LDL_C >= 155):
            score += 1
            source.append(" Cholesterol LDL 4,0-4,9 mmol/l (155-189 mg/dl) , score +1 ")

        if (dataFromText.checkAdHocTextR("Mutacja.{0,10}(?:LDLR|APOB|PCSK9)", "Mutacja genu LDLR, APOB lub PCSK9") > 0):
            score += 1
            source.append(" Mutacja genu LDLR, APOB lub PCSK9  ")

        if (dataFromText.checkAdHocTextR("Rozpoznanie hipercholesterolemii rodzinnej", "Hipercholesterolemia w rodzinie") > 0 or dataFromText.checkAdHocTextR("[Hh]ipercholesterolemia w rodzinie", "Hipercholesterolemia w rodzinie") > 0):
            score += 1
            source.append(" Rozpoznanie hipercholesterolemii rodzinnej Pewne, score +8 ")

        elif (dataFromText.checkAdHocTextR("Prawdopodobne Rozpoznanie hipercholesterolemii rodzinnej", "Rozpoznanie hipercholesterolemii rodzinnej Prawdopodobne") > 0 or dataFromText.checkAdHocTextR("Prawdopodobna [Hh]ipercholesterolemia w rodzinie", "Rozpoznanie hipercholesterolemii rodzinnej Prawdopodobne") > 0):
            score += 1
            source.append(" Rozpoznanie hipercholesterolemii rodzinnej Prawdopodobne, score +7 ")

        elif (dataFromText.checkAdHocTextR("Niepotwierdzone Rozpoznanie hipercholesterolemii rodzinnej", "Rozpoznanie hipercholesterolemii rodzinnej Niepotwierdzone") > 0 or dataFromText.checkAdHocTextR("Niepotwierdzona [Hh]ipercholesterolemia w rodzinie", "Rozpoznanie hipercholesterolemii rodzinnej Niepotwierdzone") > 0):
            score += 1
            source.append(" Rozpoznanie hipercholesterolemii rodzinnej Niepotwierdzone, score +2 ")
        return score, source
