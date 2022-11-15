from unittest import TestCase

from recommendation.dataExtractors.dataDefinitions import dataDefinitionEntries
from recommendation.processStep.GetDataOutOfNorms import GetDataOutOfNorms


class TestGetDataOutOfNorms(TestCase):

    def test_norms_various(self):
        normalez = GetDataOutOfNorms()

        unitDefinitions = "mln/mm2 {norm: M[13,inf):[4.2,5.4),F[13,inf):[3.5,5.2),d[0,8):[4.5,6],d[8,15):[4.4,5.7],d[15,31):[4.1,5.5],d[31,61):[3.4,5.1],d[61,181):[3.7,4.4],d[181,271):[3.8,5.3],d[271,365):[3.9,5.4],[1,8):[4.3,5.5],[8,13):[4.4,5.5]} "
        age_in_years = 15
        age_in_days = age_in_years * 365
        centile = 90

        self.assertTrue(normalez.valueNotInNorms(age_in_days, age_in_years, "F", centile, unitDefinitions, 5.3)[0])
        self.assertTrue(normalez.valueNotInNorms(age_in_days, age_in_years, "F", centile, unitDefinitions, 2)[0])
        self.assertTrue(normalez.valueNotInNorms(age_in_days, age_in_years, "F", centile, unitDefinitions, 6)[0])
        self.assertFalse(normalez.valueNotInNorms(age_in_days, age_in_years, "M", centile, unitDefinitions, 5.3)[0])

        age_in_years = 13
        age_in_days = age_in_years * 365
        self.assertFalse(normalez.valueNotInNorms(age_in_days, age_in_years, "M", centile, unitDefinitions, 4.3)[0])
        self.assertTrue(normalez.valueNotInNorms(age_in_days, age_in_years, "M", centile, unitDefinitions, 4.1)[0])

        age_in_years = 12
        age_in_days = age_in_years * 365
        self.assertTrue(normalez.valueNotInNorms(age_in_days, age_in_years, "M", centile, unitDefinitions, 4.3)[0])
        self.assertFalse(normalez.valueNotInNorms(age_in_days, age_in_years, "M", centile, unitDefinitions, 4.4)[0])

    def test_norms_centiles(self):
        normalez = GetDataOutOfNorms()

        unitDefinitions = "mm/Hg {norm: [19,inf):[80,84],F[0,4)c[0,90):[0,64],F[4,5)c[0,90):[0,64],F[5,6)c[0,90):[0,65],F[6,7)c[0,90):[0,66],F[7,8)c[10,90):[50,69],F[8,9)c[10,90):[51,70],F[9,10)c[10,90):[51,71],F[10,11)c[10,90):[52,71],F[11,12)c[10,90):[53,72],F[12,14)c[10,90):[54,73],F[14,15)c[10,90):[55,74],F[15,17)c[10,90):[56,74],F[17,18)c[10,90):[56,75],F[18,19)c[10,90):[57,75],M[0,3)c[0,90):[0,62],M[3,4)c[0,90):[0,63],M[4,5)c[0,90):[0,64],M[5,6)c[0,90):[0,65],M[6,7)c[0,90):[0,66],M[7,8)c[10,90):[50,68],M[8,9)c[10,90):[50,69],M[9,11)c[10,90):[51,70],M[11,13)c[10,90):[51,71],M[13,14)c[10,90):[53,72],M[14,15)c[10,90):[53,73],M[15,16)c[10,90):[55,74],M[16,17)c[10,90):[55,76],M[17,18)c[10,90):[56,76],M[18,19)c[10,90):[56,77]}"
        age_in_years = 3
        age_in_days = age_in_years * 365
        centile = 80

        self.assertFalse(normalez.valueNotInNorms(age_in_days, age_in_years, "F", centile, unitDefinitions, 5.3)[0])

    def test_allnorms_format(self):
        normalez = GetDataOutOfNorms()

        for entry in dataDefinitionEntries.values():
            unitDefinitions = entry[3]
            age_in_years = -10
            age_in_days = age_in_years * 365
            centile = -80

            print(normalez.valueNotInNorms(age_in_days, age_in_years, "F", centile, unitDefinitions, 5.3)[0])
