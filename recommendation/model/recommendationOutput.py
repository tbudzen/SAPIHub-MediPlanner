from recommendation.model.diagnosis import Diagnosis
from recommendation.model.treatment_plan import TreatmentPlan


class RecommendationOutput(object):
    def __init__(self) -> None:
        self.diagnosis: Diagnosis = None
        self.treatmentPlan: TreatmentPlan = None
