import re

from recommendation.aux.service.TraceLog import TraceLog
from recommendation.processStep.ProcessStep import ProcessStep
from recommendation.schemes.EpicrisisScheme import EpicrisisScheme


class GenerateEpicrisis(ProcessStep):

    def getStepIdentification(self):
        return "GenerateEpicrisis"

    def perform(self, payload) -> None:
        payload.status = "GenerateEpicrisis"
        epicrisisScheme = EpicrisisScheme()

        sex = payload.patientData.plec
        age = payload.patientData.wiek
        glowne_objawy_wywiad = ""
        try:
            for wywiad in payload.patient.interviews:
                if wywiad["type"] == "PODMIOTOWY" and wywiad["inScope"] and glowne_objawy_wywiad == "":
                    glowne_objawy_wywiad = wywiad["content"]
                    glowne_objawy_wywiad = "<br><br><i>" + re.sub('[Pp]acjent(ka){0,1} (w wieku)*[ ]*lat \d+,*', '', glowne_objawy_wywiad) + "</i><br>"
        except:
            glowne_objawy_wywiad = " <b>[główne objawy z wywiadu]</b>"

        glowne_odchylenie_od_normy_przedmiotowy = ""
        try:
            for wywiad in payload.patient.interviews:
                if wywiad["type"] == "PRZEDMIOTOWY" and wywiad["inScope"] and glowne_odchylenie_od_normy_przedmiotowy == "":
                    glowne_odchylenie_od_normy_przedmiotowy = "<br><i>" + wywiad["content"] + "</i><br>"
        except:
            glowne_odchylenie_od_normy_przedmiotowy = "<b>[główne odchylenie od normy z badania przedmiotowego]</b>"

        abnormalResults = payload.abnormalResults
        prescribedDrugs = " <b>[zmienione leczenie - jakie leki]</b>"
        lastTreatmentPlan = "<br><b> Podsumowanie zaleceń:</b></br><br>" + payload.treatment_plan
        try:
            payload.patient.treatmentPlans[len(payload.patient.treatmentPlans) - 1]["content"]
        except:
            TraceLog().add(payload.patient.patientIdentifier, " no tratment plan sent in the epicris request, generating a new one")
        payload.epicrisis = epicrisisScheme.generate(sex, age, glowne_objawy_wywiad, glowne_odchylenie_od_normy_przedmiotowy, abnormalResults, prescribedDrugs, lastTreatmentPlan)
