# https://pl.wikipedia.org/wiki/Skala_HAS-BLED
# https://docs.google.com/document/d/1ZmHmr6CDJMU5bTAuFiVVxAnPSx_AY9Aw1r1wtukjXrY/edit
from recommendation.classifiers.MedicalDataMapper import getfloat, MedicalDataMapper
from recommendation.processStep.ExtractDataFromText import ExtractAdditionalDataFromText


class HAS_BLED(object):

    def __init__(self, payload, patientData) -> None:
        self.extractor = MedicalDataMapper(payload)
        self.patientData = patientData
        self.payload = payload
        self.dataFromText = ExtractAdditionalDataFromText(payload, patientData)

    def calculateFromPatientData(self):

        score = 0
        source = []
        wiek = self.patientData.wiek
        dataFromText = self.dataFromText

        # H	Hypertension	nadciśnienie tętnicze	SBP>160mmHg

        if (self.patientData.cisnienie_skurczowe > 160):
            score += 4
            source.append("nadciśnienie tętnicze	SBP>160mmHg, score +1")
        # Abnormal
        # renal function
        #
        # nieprawidłowa funkcja nerek	przewlekła dializoterapia, stan po przeszczepieniu nerki lub stężenie kreatyniny w surowicy >200 µmol/l (2.26 mg/dL)

        extractor = self.extractor
        if (getfloat(extractor.getOptionalMedicalEntry("kreatynina") >= 2.26)
                or (dataFromText.checkAdHocTextR("przewlekła dializoterapia", "przewlekła dializoterapia") > 0)
                or (dataFromText.checkAdHocTextR("przeszczep.{0,10} nerki", "przeszczep nerki") > 0)
        ):
            score += 1
            source.append(" nieprawidłowa funkcja nerek	przewlekła dializoterapia, stan po przeszczepieniu nerki lub stężenie kreatyniny w surowicy >200 µmol/l (2.26 mg/dL) , score +1 ")

        # nieprawidłowa funkcja wątroby	przewlekła choroba wątroby (np. marskość) lub cechy biochemiczne istotnego uszkodzenia
        #        wątroby (np. bilirubina >2 × ggn + ALT/AST/fosfataza zasadowa >3 × ggn)
        #

        if (getfloat(extractor.getOptionalMedicalEntry("bilirubina") >= 2 * extractor.getOptionalMedicalEntry("ggn") and
                     getfloat(extractor.getOptionalMedicalEntry("ALT") >= 3 * extractor.getOptionalMedicalEntry("ggn")
                              )
                     or (dataFromText.checkAdHocTextR("przewlekła choroba wątroby ", "przewlekła choroba wątroby") > 0)
                     or (dataFromText.checkAdHocTextR("marskość", "marskość wątroby") > 0)
                     or (dataFromText.checkAdHocTextR("uszkodzenie wątroby", "uszkodzenie wątroby") > 0))):
            score += 1
            source.append(" przewlekła choroba wątroby (np. marskość) lub cechy biochemiczne istotnego uszkodzenia wątroby (np. bilirubina >2 × ggn + ALT/AST/fosfataza zasadowa >3 × ggn), score +1 ")

        # Stroke	Udar mózgu
        if (extractor.getOptionalMedicalEntry("udar_mozgu") > 0 or (dataFromText.checkAdHocTextR("udar mózgu", "udar mózgu") > 0)):
            score += 1
            source.append(" udar mózgu , score +1 ")

        # predyspozycja do krwawień	krwawienie w wywiadzie i/lub predyspozycja do krwawień (np. skaza krwotoczna, niedokrwistość itd.)

        if ((dataFromText.checkAdHocText("skaza krwotoczna") > 0)
                or dataFromText.checkAdHocText("niedokrwistość") > 0
                or dataFromText.checkAdHocText("predyspozycja do krwawień") > 0
                or dataFromText.checkAdHocText("	krwawienie w wywiadzie") > 0
        ):
            score += 1
            source.append(" predyspozycja do krwawień	krwawienie w wywiadzie i/lub predyspozycja do krwawień (np. skaza krwotoczna, niedokrwistość itd.), score +1 ")

        # niestabilne wartości INR	wahające się duże wartości lub często poza przedziałem terapeutycznym (np. >40% oznaczeń)

        if ((dataFromText.checkAdHocText("niestabilne wartości INR") > 0)
                or dataFromText.checkAdHocText("Labile INRs") > 0
                or dataFromText.checkAdHocText("predyspozycja do krwawień") > 0
                or extractor.getOptionalMedicalEntry("INR") > 2
        ):
            score += 1
            source.append("niestabilne wartości INR	wahające się duże wartości lub często poza przedziałem terapeutycznym (np. >40% oznaczeń) , score +1 ")

        # podeszły wiek	wiek >65 r.ż.

        if (wiek > 65):
            score += 1
            source.append("wiek >65 r.ż. , score +1 ")

        # przyjmowanie leków z grupy NLPZ

        if (dataFromText.checkAdHocText("przyjmuje NLPZ") > 0):
            score += 1
            source.append("przyjmowanie leków z grupy NLPZ , score +1 ")

        # Nadużywanie alkoholu

        if (dataFromText.checkAdHocText("alkohol") > 0):
            score += 1
            source.append("Nadużywanie alkoholu, score +1 ")

        return score, source
