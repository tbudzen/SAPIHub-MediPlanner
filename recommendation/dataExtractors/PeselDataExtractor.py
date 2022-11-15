import datetime

from dateutil.utils import today


class PeselDataExtractor(object):

    def __init__(self):
        pass

    def extractAgeinDaysAndGender(self, pesel: str):
        age, dateOfBirth = self.extractDateOfBirthAndGender(pesel)
        delta = today().today() - dateOfBirth
        return age, delta.days

    def extractDateOfBirthAndGender(self, pesel: str):
        weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 1]

        sum = 0
        for index in range(11):
            sum += weights[index] * int(pesel[index])
        if sum % 10 != 0:
            raise ValueError("Invalid pesel")
        year = 1900 + int(pesel[0]) * 10 + int(pesel[1])
        if (int(pesel[2]) > 1 and int(pesel[2]) < 8):
            year += int(int(pesel[2]) / 2) * 100
        if (int(pesel[2]) >= 8):
            year -= 100
        month = (int(pesel[2]) % 2) * 10 + int(pesel[3])
        day = int(pesel[4]) * 10 + int(pesel[5])
        gender = "MALE" if (int(pesel[9]) % 2 == 1) else "FEMALE"
        return (gender, datetime.datetime(year=year, month=month, day=day))
