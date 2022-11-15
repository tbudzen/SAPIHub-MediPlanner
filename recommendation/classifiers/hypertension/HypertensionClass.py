class HypertensionClass(object):

    def determineClass(self, sys, dia) -> int:
        systolic_category = int((sys - 110) / 10) - 2 if sys < 140 else int((sys - 140) / 20) + 1
        diastolic_category = int((dia - 75) / 5) - 2 if dia < 90 else int((dia - 90) / 10) + 1
        return min(3, max(-2, systolic_category, diastolic_category))

    def isIsolatedSystolic(self, sys, dia) -> bool:
        return sys >= 140 and dia < 90
