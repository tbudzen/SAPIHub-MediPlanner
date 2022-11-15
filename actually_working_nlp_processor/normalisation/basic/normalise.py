# normalizuje wedlug slownika <dict.tsv>


class Normalisation():
    annoCache = {}

    nlp = None

    def __init__(self, nlp0):
        self.nlp = nlp0

    def normalise(self, text: str, ann_names_crf: str, dictPath: str) -> str:
        lemmatise = True
        normDict = {}
        namesDict = {}
        try:
            for line in open(dictPath, encoding="utf-8", errors='ignore'):
                parts = line.split("\t")
                text = parts[0]
                icd = parts[1]
                name = parts[4].strip()
                normDict[text] = icd
                if name != "":
                    namesDict[icd] = name
            # normDict[name.lower()]=icd
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError in normalise.py")

        print("Read " + str(len(namesDict)) + " different codes.")

        def canonise(text):
            text = text.lower().replace(".", "").replace(",", "")
            if lemmatise:
                if not text in self.annoCache:
                    self.annoCache[text] = " ".join([token.lemma_ for token in self.nlp(text)])
                text = self.annoCache[text]
            return (text)

        out = ""
        counter = 1
        try:
            for line in ann_names_crf.splitlines():
                if not (line.startswith("T") and line[1].isdigit() and len(line.split("\t")) == 3):
                    continue
                tid = line.split("\t")[0]
                text = canonise(line.split("\t")[2].strip())
                parts = text.split(" ")
                for i in range(len(parts)):
                    partsin = parts[0:(len(parts) - i)]
                    shorttext = " ".join(partsin)
                    # if len(shorttext)<=0.5*len(text):
                    #	break
                    if shorttext in normDict:
                        name = ""
                        icd = normDict[shorttext]
                        if icd in namesDict:
                            name = namesDict[icd]
                        out += ("N" + str(counter) + "\tReference " + tid + " " + icd + "\t" + name + "\n")
                        counter = counter + 1
                        break
            print("Normalisations added: " + str(counter - 1))
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError: " + str(e))
        return out
