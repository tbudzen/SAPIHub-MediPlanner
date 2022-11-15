class AdditionalDataVars(object):

    def __init__(self, payload, patientData) -> None:
        self.patientData = patientData
        self.payload = payload

    def initData(self):
        self.patientData.region_pochodzenia = {
            'Europa': 1.0,
            'Azja Poludniowa': 1.4,
            'Afryka subsaharyjska': 1.3,
            'Region Karaibow': 1.3,
            'Azja Zachodnia': 1.2,
            'Afryka Polnocna': 0.9,
            'Azja Wschodnia': 0.7,
            'Ameryka Poludniowa': 0.7
        }

        #hardwired for starters
        self.patientData.region_pochodzenia_pacjenta = self.patientData.region_pochodzenia['Europa']