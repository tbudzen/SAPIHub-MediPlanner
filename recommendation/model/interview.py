from recommendation.model.treatment_plan import TreatmentPlan


class Interview(object):
    def __init__(self) -> None:
        self.date = None
        self.text = None
        self.text_id = None
        self.type = None
        self.treatment_plan:TreatmentPlan = None
