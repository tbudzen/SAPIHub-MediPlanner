from actually_working_nlp_processor.conf import NLP_ROOT
from actually_working_nlp_processor.crf.conversion.conversion import ConversionUtils, MeshPolTag


class CrfConversion():

    def __init__(self, nlp):
        self.nlp = nlp
        # PARAMS
        PREFIX = NLP_ROOT + "crf/conversion/"
        isMeshPolsFromCache = True
        isMedicinesFromCache = True

        # INPUT FILES

        distinctMeshPolTags = PREFIX + "distinctMeshPolTags.txt"
        meshpolFile = PREFIX + "meshpol.tsv"
        meshpolFileCache = PREFIX + "meshpol_cache.json"
        medicinesFile = PREFIX + "rpo.tsv"
        medicinesFileCache = PREFIX + "medicines_cache.json"

        self.myconv = ConversionUtils(self.nlp)

        self.selectedMeshPolTags = list(map(lambda line: MeshPolTag(line),
                                            self.myconv.linesFromFile(distinctMeshPolTags)))
        print(len(self.selectedMeshPolTags))

        self.meshPols = self.myconv.getMeshPols(isMeshPolsFromCache, meshpolFile, self.selectedMeshPolTags, meshpolFileCache)
        self.medicines = self.myconv.getMedicines(isMedicinesFromCache, medicinesFile, medicinesFileCache)

    def my_conversion(self, inputText, keep_tags) -> str:

        def tokenToLine(tokenInfo, keepTags, headerTag):
            token = tokenInfo.token
            cells = []
            cells.append(token.text.strip())
            cells.append(token.lemma_.strip())
            cells.append(token.tag_)
            cells.append(tokenInfo.getFirstMeshPolTagStr())
            cells.append(tokenInfo.getMedicineTagCell())
            cells.append(headerTag)
            if keepTags:
                cells.append(tokenInfo.tag)
            else:
                cells.append(str(tokenInfo.startIndex))
                cells.append(str(len(token.text)))
            emptyLine = ""
            if tokenInfo.isLastInSentence:
                emptyLine = "\n"
            return "\t".join(cells) + "\n" + emptyLine

        # PARAMS

        if keep_tags == '1':
            keepTags = True
        else:
            keepTags = False

        tags = []
        text = inputText.replace("\\x0a", "\n   ")
        tokens = self.myconv.tokensFromAnnotations1(text, tags, self.selectedMeshPolTags)
        tokens = self.myconv.updateWithMeshTags(tokens, self.meshPols, list(map(lambda meshTag: meshTag.name, self.selectedMeshPolTags)))
        tokens = self.myconv.updateWithMedicines(tokens, self.medicines)
        output = ""  # feaures
        prevHeader = ""
        currHeader = None
        currSpaces = 0
        for token in tokens:
            # check the current header
            headerTag = "o"
            if token.token.text.startswith("-----"):
                if currHeader is None:
                    currHeader = ""
                prevHeader = currHeader
                currHeader = None
                currSpaces = 0
            elif token.token.tag_ == "_SP":
                currSpaces = currSpaces + 1
                if currSpaces == 3:
                    currHeader = ""
            elif currHeader is None:
                currHeader = token.token.text.strip().lower()
            # add previous header to features
            if prevHeader != "" and not token.token.text.startswith("-----") and not currHeader is None:
                headerTag = "i-" + prevHeader
            # write it out
            line = tokenToLine(token, keepTags, headerTag)
            try:
                output += line
            except UnicodeEncodeError as e:
                print("myconversion: UnicodeEncodeError")
        output += "\n"
        return output
