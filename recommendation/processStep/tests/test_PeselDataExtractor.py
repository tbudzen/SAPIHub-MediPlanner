from unittest import TestCase

from recommendation.dataExtractors.PeselDataExtractor import PeselDataExtractor


class TestPeselDataExtractor(TestCase):
    def test_extract_date_of_birth_and_gender(self):
        de = PeselDataExtractor()

        gender, dateOfBirth = de.extractDateOfBirthAndGender("90090263555")
        self.assertEqual(dateOfBirth.strftime("%b %d %Y"), "Sep 02 1990")
        self.assertEqual(gender, "MALE")

        gender, dateOfBirth = de.extractDateOfBirthAndGender("18311706511")
        self.assertEqual(dateOfBirth.strftime("%b %d %Y"), "Nov 17 2018")
        self.assertEqual(gender, "MALE")

        gender, numberOfDays = de.extractAgeinDaysAndGender("20311807970")

        self.assertTrue(numberOfDays >= 1)
