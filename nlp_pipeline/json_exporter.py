# Converts .ann file to JSON file

from collections import defaultdict

import os.path
import json
import sys

    # plik *.ann -> {"annotations":{ {anotacja1}, {anotacja2}, ... },  "originalText":originalText }
    # ---
    # sample:
    #
    # {"annotations":
    #   {
    #       {"type":"T", "identifier":"T17" "subtype":"Condition", "value": "Wrodzona wada serca pod postaci¹ zwê¿enia cieni aorty", "position":[438,492]},
    #       {"type":"N", "identifier":"N1", "subtype":"Reference", "referenced": "T1", "value":"ICD10:Q25.1	Zwê¿enie cieni aorty"},
    #       {"type":"A", "identifier:"A1", "subtype": "Source", "referenced": "T10", "value": "Declared"},
    #      ...
    #   },
    #   "originalText":"Lorem ipsum...."
    # }

class JSONExporter():

    def convert(self, ann_file, txt_file, json_file):

        anndict = defaultdict(dict)

        with open(ann_file, encoding='utf-8', errors='ignore') as f:

            try:
                for index, line in enumerate(f):

                    begin = line.rstrip().split("\t")[0]
                    rest = line.rstrip().split("\t")[1:]

                    try:
                        anndict[begin] = u"\t".join(rest)
                    except IndexError:
                        print('JSONExporter.convert() error: Index error while reading ann file - ' + ann_file)
                        continue
            except UnicodeDecodeError as e:
                pass

        #print(str(anndict))

        d = defaultdict()
        d["annotations"] = []

        #print("cwd, jsone.txt_file is " + os.getcwd() + ", " + txt_file)

        sf_txt = ""
        sf = open("test_output_attributes/" + txt_file, encoding="utf-8", errors='ignore')
        try:
            sf_txt = sf.read()
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError in JSONExporter.convert().")
        sf.close()

        d["originalText"] = sf_txt

        for k in anndict.keys():

            #print("Anndict key = " + str(k))

            d2 = defaultdict() # For single entity

            p = anndict[k].split(u"\t") # Entity parts
            p0_split = p[0].split(' ')

            if len(k) > 0:
                entity_type = k[0] # Single entity type char

                if entity_type == "T":

                    # T* ->
                    #     {"type":"T", "identifier":"T17" "subtype":"Condition", "value": "Wrodzona wada serca pod postaci¹ zwê¿enia cieni aorty", "position":[438,492]}
                    #     {"type":"T", "identifier":"T3" "subtype":"Date", "value": "29.09.1999", "oryginalValue":"w dniu badania", "position":[438,492]}
                    #
                    #     * uwagi:
                    #      -standaryzacja dat tekstowych do formatu ddd-MM-YYYY, MM-YYYY, b¹d YYYY, np "w chwili obecnej"-> data badania, wartoæ oryginalna zachowana, mo¿e mieæ to szczególne znaczenie w przypadku analizy aktualnych objawó
                    #      -subtypes: Condition, Date, Negation, Drug, Treatment, Investigation, Drug_dose etc.

                    d2["type"] = "T"
                    d2["identifier"] = k
                    d2["subtype"] = p0_split[0]
                    if len(p) > 1:
                        if d2["subtype"] == "Date": # Canonical form taken from annotation_processor's date recognition
                            d2["value"] = p[1]
                        else:
                            d2["value"] = p[1]
                    #print('p = ', str(p))
                    if len(p0_split) > 2:
                        d2["position"] = [p0_split[1], p0_split[2]]

                elif entity_type == "N":

                    # N* -> {"type":"N", "identifier":"N1", "subtype":"Reference", "referenced": "T1", "value":"ICD10:Q25.1	Zwê¿enie cieni aorty"}

                    d2["type"] = "N"
                    d2["identifier"] = k
                    d2["subtype"] = p0_split[0]
                    d2["referenced"] = p0_split[1]
                    d2["icd"] = p0_split[2]
                    if len(p) > 1:
                        d2["value"] = p[1]
                    else:
                        d2["value"] = ""

                elif entity_type == "R":

                    # R* -> {"type":"R", "identifier":"R1", "subtype":"Dat", "arg1":"T18", "arg2":"T16"}
                    #     * uwagi:
                    #      - subtypes:Dat, Neg, etc

                    d2["type"] = "R"
                    d2["identifier"] = k
                    d2["subtype"] = p0_split[0]
                    d2["arg1"] = p0_split[1].split(":")[1]
                    d2["arg2"] = p0_split[2].split(":")[1]

                elif entity_type == "A":

                    # A* -> {"type":"A", "identifier:"A1", "subtype": "Source", "referenced": "T10", "value": "Declared"}
                    #     * uwagi:
                    #      - subtypes:Source, Status, etc

                    #print("A: " + str(p0_split))
                    d2["type"] = "A"
                    d2["identifier"] = k
                    d2["subtype"] = p0_split[0]
                    d2["referenced"] = p0_split[1]
                    d2["value"] = p0_split[2]

                else:

                    print("JSONExporter.convert() error: Unknown entity type - " + k + " = " + str(anndict[k]))

            d["annotations"].append(d2)

        f = open("test_output_attributes/" + os.path.basename(ann_file).split('.')[0] + ".json", "w", encoding="utf-8", errors='ignore')
        s = json.dumps(d, sort_keys=True, indent=4)
        f.write(s)
        f.close()

        return s

if __name__ == "__main__":
    cnt = len(sys.argv)
    if cnt == 2:
        filepath = sys.argv[1]
        jsone = JSONExporter()
        jsone.convert(filepath, "", "out.json")
