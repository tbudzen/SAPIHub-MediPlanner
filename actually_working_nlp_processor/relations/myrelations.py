from actually_working_nlp_processor.relations.relations import RelationsUtils


class TheRelations():
    nlp = None

    def __init__(self, nlp0):
        self.nlp = nlp0

    def process_relations(self, text: str, stripped: str) -> str:
        out = ""
        ru = RelationsUtils(self.nlp)
        tags = ru.tagsFromAnn(stripped)

        out += stripped

        try:
            (relations, sentences) = ru.findSuspectRelations(tags, text)
            # print(str(relations))
            ru.removeRedundantRelations(relations, sentences, 2)
            relations = list(filter(lambda relation: not relation.removed, relations))
            print("Adding " + str(len(relations)) + " relations...")
            out += ru.appendRelationsToStr(relations)
        except AttributeError as e:
            print("AttributeError: " + str(e))

        # process finished
        return out
