import os
import datetime 
import codecs

from datetime import date
from datetime import datetime
from nlp_pipeline.attributes.age_sex_importer import  AgeSexImporter

from io import open

from collections import OrderedDict, defaultdict
from nlp_pipeline.attributes.annotation import Annotation

from dateutil.relativedelta import relativedelta

from nltk.tokenize import wordpunct_tokenize

def processann(mode, pathtofile, age, sex, status_rfc, status_bc, source_bc, dataset_source_file, dataset_status_file_1, dataset_status_file_2, date_errors_file, date_bc):
    """
    Import ann and .txt files from a folder.

    :param pathtofile: (string) the path to the folder containing both the
    .ann and .txt files.
    :return: a tuple containing a dictionary of annotations and a string,
    representing the text of the document
    """

    annotations = readannfile(mode, pathtofile, age, sex, status_rfc, status_bc, source_bc, dataset_source_file, dataset_status_file_1, dataset_status_file_2, date_errors_file, date_bc)

def _join(annotations, sentences):
    """
    join a list of annoations with a list of sentences.

    :param annotations: list of annotations
    :param sentences:
    :return:
    """
    for ann in annotations:
        for span in ann.spans:

            begin, end = span

            for s in sentences:
                words = s.getwordsinspan(begin, end)
                ann.words.extend(words)
                for w in words:
                    w.annotations.append(ann)


def _createannotationobjects(annotations):
    """
    Create instances of the Annotation class for each of the "T" annotations.

    Input is assumed to only be "T" annotations.

    :param annotations: (dict) dictionary of "T" annotations.
    :return: (OrderedDict) an ordered dictionary of Annotations objects.
    Length of this dictionary should be equal to the input dictionary.
    """
    targets = OrderedDict()

    for key, t in annotations.items():
        splitted = t.split("\t")
        t = splitted[0]
        repr = u" ".join(splitted[1:])

        split = t.split()
        label = split[0]

        try:
            spans = [[int(span.split()[0]), int(span.split()[1])]
                 for span in u" ".join(split[1:]).split(";")]

            targets[key] = Annotation(key, repr, spans, [label])
        except IndexError:
            dummy = 0
    return targets


def _find_t(e, annotations):
    """
    Given an "E" annotation from an .ann file, find the "T" annotation.

    Because "E" annotations can be nested, the search should be done on deeper
    levels.

    :param e: (string) the "E" annotation we want to find the target of.
    :param annotations: (dict) the dict of annotations.
    :return: the keys of "T" annotations this e annotation points to.
    """
    e = e.split()
    keys = []

    if len(e) > 1:

        targetkeys = [y for y in [x.split(":")[1] for x in e[1:]]]

        for key in targetkeys:
            if key[0] == "E":
                keys.append(annotations['E'][key[1:]].split()[0].split(":")[1])

            if key[0] == "T":
                keys.append(key)

    return keys

def is_number(s): # for future expansion

    result = s.isdigit()

    return result

def is_date_part_separator(s): # for future expansion

    if s=="/" or s=="\\" or s==".":
        return True
    else:
        return False

def calc_date(s, age, date_errors_file):

    # For each pattern find first, max., pattern matching phrase and calculate date

    # 1) Tokenize s

    s = s.lower()
    
    tokens = wordpunct_tokenize(s)

    # Split year and 'r'

    i = 0
    for token in tokens:
        if len(token) >= 2:
            if token[-1] == 'r' and is_number(token[0:len(token)-2]):
                tokens[i] = tokens[i][0:len(tokens[i]) - 1]
        if tokens[i] == "," or tokens[i] == ";" or tokens[i] == "(" or tokens[i] == ")" or tokens[i] == "[" or tokens[i] == "]":
            tokens[i] = ""
        i += 1

    if tokens[len(tokens) - 1] == "." or tokens[len(tokens) - 1] == ")." or tokens[len(tokens) - 1] == ".)":
        tokens[len(tokens) - 1] = ""

    # Reduce [""] from the right side, "r" already replaced by ""

    t = []
    for token in tokens:
        if token != "":
            t.append(token)


    d = date.today() # default
    #d = d.replace(year=d.year - 15) # todo - heuristic <-- Too many Errors!

    canonical_form = d.strftime("%d-%m-%Y") # For each rule distinct assignment for future use maybe

    # 2) Match pattern

    pattern_found = False

    # Was error - multiple elif instead of single if-s
    try:

        # od kilku tygodni

        if not pattern_found and s == "od kilku tygodni":
            d = datetime.today() - relativedelta(months =- 2)
            d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
            canonical_form = d.strftime("%d-%m-%Y")
            pattern_found = True

        # od kilku lat

        if not pattern_found and s == "od kilku lat":
            d = datetime.today()
            d = d.replace(year=d.year - 5)
            d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
            canonical_form = d.strftime("%Y")
            pattern_found = True

        # od miesiąca

        if not pattern_found and (s == "od miesiąca" or s == "w ostatnim miesiącu"):
            d = datetime.today() - relativedelta(months =- 1)
            d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
            canonical_form = d.strftime("%m-%Y")
            pattern_found = True

        # od dwóch miesięcy

        if not pattern_found and (s == "od dwóch miesięcy"):
            d = datetime.today() - relativedelta(months =- 2)
            d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
            canonical_form = d.strftime("%m-%Y")
            pattern_found = True

        # od kilku miesięcy

        if not pattern_found and (s == "od kilku miesięcy"):
            d = datetime.today() - relativedelta(months =- 6)
            d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
            canonical_form = d.strftime("%m-%Y")
            pattern_found = True

        # kilka lat temu

        if not pattern_found and (s == "kilka lat temu" or s == "od wielu lat"):
            d = datetime.today()
            d = d.replace(year=d.year - 5)
            d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
            canonical_form = d.strftime("%Y")
            pattern_found = True

        # N
        # Check for year from the right side
        if not pattern_found and len(t) > 0:
            if is_number(t[len(t) - 1]) and len(t[len(t) - 1]) == 4:
                d = datetime.strptime(t[len(t) - 1], '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # N r
        if not pattern_found and len(t) >= 2:
            if t[len(t) - 1] == "r" and is_number(t[len(t) - 2]) and len(t[len(t) - 2]) == 4:
                d = datetime.strptime(t[len(t) - 2], '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True


        # Check for year with "roku" (f.e. w 1999 roku) from the right side
        if not pattern_found and len(t) >= 2:
            if is_number(t[len(t) - 2]) and len(t[len(t) - 2]) == 4 and t[len(t)-1]=="roku":
                d = datetime.strptime(t[len(t) - 2], '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True
        
        # N

        if not pattern_found and len(t) == 1:
            if is_number(t[0]):
                if len(t[0]) == 2:
                    t[0] = "20" + t[0]
                d = datetime.strptime(t[0], '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True
        
        # N lat

        if not pattern_found and len(t) >= 2:
            if t[len(t) - 1] == "lat" and is_number(t[len(t) - 2]):
                n = int(t[len(t) - 2])
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # od kilku miesięcy

        if not pattern_found and len(t) >= 3:
            if t[len(t) - 1] == "miesięcy" and t[len(t) - 2] == "kilku" and t[len(t) - 3] == "od":
                n = 6
                d = datetime.today() - relativedelta(months =- n)
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%m-%Y")
                pattern_found = True

        # od N miesięcy

        if not pattern_found and len(t) >= 3:
            if t[len(t) - 1] == "miesięcy" and is_number(t[len(t) - 2]) and t[len(t) - 3] == "od":
                n = int(t[len(t) - 2])
                d = datetime.today() - relativedelta(months =- n)
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%m-%Y")
                pattern_found = True

        # N miesięcy

        if not pattern_found and len(t) >= 2:
            if t[len(t) - 1] == "miesięcy" and is_number(t[len(t) - 2]):
                n = int(t[len(t) - 2])
                d = datetime.today() - relativedelta(months =- n)
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%m-%Y")
                pattern_found = True

        # rok temu

        if not pattern_found and len(t) >= 2:
            if t[len(t) - 1] == "temu" and t[len(t) - 2] == "rok":
                d = datetime.strptime(str(date.today().year - 1), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True
        
        # od(do) roku

        if not pattern_found and len(t) >= 2:
            if (t[len(t) - 1] == "od" or t[len(t) - 1] == "do") and t[len(t) - 2] == "roku":
                d = datetime.strptime(str(date.today().year - 1), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # w N, od N, do N

        if not pattern_found and len(t) >= 2: 
            if (t[len(t) - 2] == "w" or t[len(t) - 2] == "od" or t[len(t) - 2] == "do") and is_number(t[len(t) - 1]):
                d = datetime.strptime(t[len(t) - 1], '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True
        
        # M / Y

        if not pattern_found and len(t) == 3:
            if is_number(t[0]) and is_date_part_separator(t[1]) and is_number(t[2]):
                if len(t[2]) == 2:
                    t[2] = "20" + t[2]
                d = datetime.strptime(t[0] + "/" + t[2], '%m/%Y').date()
                canonical_form = d.strftime("%m-%Y")
                pattern_found = True
        
        # D / M / Y

        if not pattern_found and len(t) >= 5:
            if is_number(t[len(t) - 1]) and is_date_part_separator(t[len(t) - 2]) and is_number(t[len(t) - 3]) and is_date_part_separator(t[len(t) - 4]) and is_number(t[len(t) - 5]):
                if len(t[len(t) - 1]) == 2:
                    t[len(t) - 1] = "20" + t[len(t) - 1]
                d = datetime.strptime(t[len(t) - 5] + "/" + t[len(t) - 3] + "/" + t[len(t) - 1], '%d/%m/%Y').date()
                canonical_form = d.strftime("%d-%m-%Y")
                pattern_found = True

        # D / M / Y .

        if not pattern_found and len(t) >= 6:
            if t[len(t)-1] == "." and is_number(t[len(t) - 2]) and is_date_part_separator(t[len(t) - 3]) and is_number(t[len(t) - 4]) and is_date_part_separator(t[len(t) - 5]) and is_number(t[len(t) - 6]):
                if len(t[len(t) - 2]) == 2:
                    t[len(t) - 2] = "20" + t[len(t) - 2]
                d = datetime.strptime(t[len(t) - 6] + "/" + t[len(t) - 4] + "/" + t[len(t) - 2], '%d/%m/%Y').date()
                canonical_form = d.strftime("%d-%m-%Y")
                pattern_found = True
        
        # D / M / Y r

        if not pattern_found and len(t) >= 6:
            if t[len(t)-1] == "r" and is_number(t[len(t) - 2]) and is_date_part_separator(t[len(t) - 3]) and is_number(t[len(t) - 4]) and is_date_part_separator(t[len(t) - 5]) and is_number(t[len(t) - 6]):
                if len(t[len(t) - 2]) == 2:
                    t[len(t) - 2] = "20" + t[len(t) - 2]
                d = datetime.strptime(t[len(t) - 6] + "/" + t[len(t) - 4] + "/" + t[len(t) - 2], '%d/%m/%Y').date()
                canonical_form = d.strftime("%d-%m-%Y")
                pattern_found = True

        # N l/lat/lata temu

        if not pattern_found and len(t) >= 3:
            if t[len(t) - 1] == "temu" and t[len(t) - 2] == "lat" and is_number(t[len(t) - 3]):
                n = int(t[len(t) - 3])
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True
            elif t[len(t) - 1] == "temu" and t[len(t) - 2] == "lata" and is_number(t[len(t) - 3]):
                n = int(t[len(t) - 3])
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True
            elif t[len(t) - 1] == "temu" and t[len(t) - 2] == "l" and is_number(t[len(t) - 3]):
                n = int(t[len(t) - 3])
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # N l/lat/lata

        if not pattern_found and len(t) >= 2:
            if t[len(t) - 1] == "lat" or t[len(t) - 1] == "lata" or t[len(t) - 1] == "l":
                if is_number(t[len(t) - 2]):
                    n = int(t[len(t) - 2])
                    d = datetime.strptime(str(date.today().year - n), '%Y').date()
                    canonical_form = d.strftime("%Y")
                    pattern_found = True

        # od N lat

        if not pattern_found and len(t) >= 3:
            if t[len(t) - 1] == "lat" and is_number(t[len(t) - 2]) and t[len(t) - 3] == "od":
                n = int(t[len(t) - 2])
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # od N

        if not pattern_found and len(t) >= 2:
            if is_number(t[len(t) - 1]) and t[len(t) - 2] == "od":
                d = datetime.strptime(str(int(t[len(t) - 1])), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # od N tygodni

        if not pattern_found and len(t) >= 3:
            if t[len(t) - 1] == "tygodni" and is_number(t[len(t) - 2]) and t[len(t) - 3] == "od":
                d = datetime.today()- relativedelta(months =- int(int(t[len(t) - 2]) / 4))
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%d-%m-%Y")
                pattern_found = True

        # od N m - cy
        # od ok . N m - cy

        if not pattern_found and len(t) >= 5:
            if t[len(t) - 1] == "cy" and t[len(t) - 2] == "-" and t[len(t) - 3] == "m" and is_number(t[len(t) - 4]):
                d = datetime.today() - relativedelta(months =- int(t[len(t) - 4]))
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%d-%m-%Y")
                pattern_found = True

        # miesiąc temu

        if not pattern_found and s == "miesiąc temu":
            d = datetime.today() - relativedelta(months =- 1)
            d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
            canonical_form = d.strftime("%d-%m-%Y")
            pattern_found = True

        # N miesięcy temu

        if not pattern_found and len(t) >= 3:
            if is_number(t[len(t) - 3]) and (t[len(t) - 2] == "miesięcy" or t[len(t) - 2] == "miesiące") and t[len(t) - 1] == "temu":
                d = datetime.today() - relativedelta(months =- int(t[len(t) - 3]))
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%d-%m-%Y")
                pattern_found = True

        # przed N miesiącami

        if not pattern_found and len(t) >= 2:
            if is_number(t[len(t) - 2]) and t[len(t) - 1] == "miesiącami":
                d = datetime.today() - relativedelta(months =- int(t[len(t) - 2]))
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%d-%m-%Y")
                pattern_found = True

        # N miesięcy

        if not pattern_found and len(t) >= 2:
            if is_number(t[len(t) - 2]) and t[len(t) - 1] == "miesięcy":
                d = datetime.today() - relativedelta(months =- int(t[len(t) - 2]))
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%d-%m-%Y")
                pattern_found = True

        # N - M miesięcy

        if not pattern_found and len(t) >= 4:
            if is_number(t[len(t) - 4]) and is_number(t[len(t) - 2]) and t[len(t) - 1] == "miesięcy":
                d = datetime.today() - relativedelta(months =- int(t[len(t) - 4]))
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%m-%Y")
                pattern_found = True

        # od N - M miesięcy

        if not pattern_found and len(t) >= 5:
            if t[len(t) - 5] == "od" and is_number(t[len(t) - 4]) and is_number(t[len(t) - 2]) and t[len(t) - 1] == "miesięcy":
                d = datetime.today() - relativedelta(months =- int(t[len(t) - 4]))
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%m-%Y")
                pattern_found = True

        # od xxx N - M miesięcy

        if not pattern_found and len(t) >= 6:
            if t[len(t) - 6] == "od" and is_number(t[len(t) - 4]) and is_number(t[len(t) - 2]) and t[len(t) - 1] == "miesięcy":
                d = datetime.today() - relativedelta(months =- int(t[len(t) - 4]))
                d = datetime.strptime(str(d.day) + "/" + str(d.month) + "/" + str(d.year), '%d/%m/%Y').date()
                canonical_form = d.strftime("%m-%Y")
                pattern_found = True

        # przed N laty

        if not pattern_found and len(t) >= 3:
            if t[len(t) - 1] == "laty" and is_number(t[len(t) - 2]) and t[len(t) - 3] == "przed":
                n = int(t[len(t) - 2])
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # N lat wstecz

        if not pattern_found and len(t) >= 3:
            if t[len(t) - 1] == "wstecz" and t[len(t) - 2] == "lat" and is_number(t[len(t) - 3]):
                n = int(t[len(t) - 3])
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # od N - M lat

        if not pattern_found and len(t) >= 5:
            if t[len(t) - 1] == "lat" and is_number(t[len(t) - 2]) and t[len(t) - 3] == "-" and is_number(t[len(t) - 4]) and t[len(t) - 5] == "od":
                n1 = int(t[len(t) - 2])
                n2 = int(t[len(t) - 4])
                n = (n1 + n2) / 2
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # w N roku życia /zycia 

        if not pattern_found and len(t) >= 4:
            if (t[len(t) - 1] == "życia" or t[len(t) - 1] == "zycia") and t[len(t) - 2] == "roku" and is_number(t[len(t) - 3]):
                x = int(t[len(t) - 3])
                year_distance = int(age) - x
                d = datetime.strptime(str(date.today().year - year_distance), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        # N lat z przerwami

        if not pattern_found and len(t) >= 3:
            if t[len(t) - 1] == "przerwami" and t[len(t) - 2] == "z" and t[len(t) - 3] == "lat" and is_number(t[len(t) - 4]):
                n = int(t[len(t) - 4])
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True


        ################################

        if not pattern_found and len(t) > 0:
            # todo based on birth date
            if t[len(t) - 1] == "noworodkowym" or t[len(t) - 1] == "dziecięcym" or t[len(t) - 1] == "dawna" or t[len(t) - 1] == "dzieciństwie" or t[len(t) - 1] == "przeszłości":
                n = 20 ############## <---------------- todo
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        if not pattern_found and (s == "w zeszłym roku" or s == "od roku" or s == "od jednego roku"):
                n = 1 ############## <---------------- todo
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        if not pattern_found and (s == "kiedyś" or s == "przed wielu laty" or s == "od wielu lat" or s == "wieloletnim"):
                n = 20 ############## <---------------- todo
                d = datetime.strptime(str(date.today().year - n), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True
    
        if not pattern_found and len(t) > 0:
            if t[len(t) - 1] == "obecnie" or t[len(t) - 1] == "obecnej" or t[len(t) - 1] == "aktualnie":
                d = datetime.today().date()
                pattern_found = True

        if not pattern_found and len(t) >= 2:
            if t[len(t) - 1] == "rokiem" or t[len(t) - 2] == "przed":
                d = datetime.strptime(str(date.today().year - 1), '%Y').date()
                canonical_form = d.strftime("%Y")
                pattern_found = True

        if not pattern_found and len(t) >= 2:
            if t[0] == "za":
                d = datetime.today().date() # todo - WARNING: should we calculate future?
                pattern_found = True

    except ValueError as e:
        print("calc_date() error: " + str(e))
        d = datetime.today().date()
        canonical_form = d.strftime("%d-%m-%Y")

    if not pattern_found:
        try:
            date_errors_file.write('[' + s + '] -> ' + str(t) + '\n')
        except UnicodeEncodeError as e:
            print('UnicodeEncodeError in calc_date(): date_errors_file.write().')
        #print('Tokens of unrecognized date pattern [' + s + '] are ' + str(t))
    #else:
    #    print('t of recognized date pattern [' + s + '] are ' + str(t))

    return (pattern_found, d, canonical_form)


def find_declared_phrase(s_txt, t_idx_start, t_idx_end):
    
    result = False

    distance = 50 # todo - value UWAGA wartość większa dała lepszy wynik (było 20 chyba)

#0.5392 dla tylko podejrz

    phrases = ["podejrz", "w kierunku", " szczepien"] # Space to avoid "wszczepienie"

    if t_idx_start > distance:
        for phrase in phrases:
            pos = s_txt.lower().find(phrase, t_idx_start - distance)
            if pos > -1 and pos < t_idx_start and t_idx_start - pos < distance:
                print('find_declared_phrase [' + str(pos) + ', ' + str(t_idx_start) + ']: ' + s_txt[pos:t_idx_start])
                result = True
                break

    return result


def map_entity_type_to_code(s):       

    dict = {
        "Drug" : 1,
        "Treatment" : 2,
        "Condition" : 3,
        "Symptom" : 4,
        "Behaviour" : 5,
        "Investigation" : 6,
        "Investigation_result" : 7,
        "Drug_dose" : 8,
        "Date" : 9
    }

    return 0 #dict.get(s) # 325 - if 0 -> 365

def get_windowed_phrase(s, s_start_idx, s_end_idx, words_l, words_r):
        
    idx_l = s_start_idx
    idx_r = s_end_idx

    #print('get_windowed_phrase(s, ' + str(s_start_idx) + ', ' + str(s_end_idx) + ')')
    
    words_l_count = 0
    words_r_count = 0

    while idx_l >= 0 and idx_l < len(s) and words_l_count < words_l:
        if s[idx_l] == "\n" or s[idx_l] == "-":
            idx_l += 1
            break
        idx_l -= 1
        if idx_l >= 0 and s[idx_l] == " ":
            words_l_count += 1

    while idx_r < len(s) and words_r_count < words_r:
        if s[idx_r] == "\n" or s[idx_r] == "-":
            idx_r -= 1
            break
        idx_r += 1
        if idx_r < len(s) and s[idx_r] == " ":
            words_r_count += 1

    #print('get_windowed_phrase: ' + s[s_start_idx:s_end_idx] + ' ==> ' + s[idx_l:idx_r])

    s2 = s[idx_l:idx_r].replace(';', '').replace('\n', '').replace('\r', '').replace('\t', ' ')

    return s2

def _process_source_annotations(mode, filename, annotations, age, sex, bc, dataset_source_file):
 
    r_start, r_end = AgeSexImporter.extract_family_record(filename.split('.')[0] + '.txt')
               
    #print("Mode is " + mode)

    if mode == "annotate":

        print('Annotating source on ' + filename + '...')

        # 0) Check for ending '/n' in the output filename

        f_out = codecs.open(filename, 'r', 'utf-8')
        s = f_out.read().rstrip()
        f_out.close()

        f_out = codecs.open(filename, 'w+', 'utf-8')
        f_out.write(s)
                    
        key = os.path.splitext(filename)[0]
        txt_file_path = key + '.txt'
        txt_in = codecs.open(txt_file_path, 'r', 'utf-8')
        try:
            s_txt = txt_in.read().rstrip()
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError in _process_source_annotations()")
        txt_in.close()

        cnt_declared = 0

        max_a_idx = 0
        for a in annotations["A"].keys():
            try:
                if int(a) > max_a_idx:
                    max_a_idx = int(a)
            except ValueError:
                print('max_a_idx: ValueError in filename ' + filename + ': ' + str(a))

        #print('Max A idx for ' + filename + ' is ' + str(max_a_idx))

#T62 Condition 2750 2759 Uczulenia
#N25 Reference T62 ICD10:Z88 Uczulenia na leki, Ĺ›rodki farmakologiczne i substancje biologiczne w wywiadzie
#T63 Drug 2773 2783  salicylany
#R28 Alg Arg1:T62 Arg2:T63   
#A3  Source T63 Declared

#T113    Drug 4365 4374  ĹĽoĹ‚Ä…dkowe
#A9  Source T113 Declared

        new_a_idx = max_a_idx

        for t in annotations["T"].keys():

            tref = t
            tval = annotations["T"][tref].split()

            if tval[0] == "Investigation" or tval[0] == "Investigation_result" or tval[0] == "Drug" or tval[0] == "Drug_dose" or tval[0] == "Date" or tval[0] == "Treatment" or tval[0] == "Condition" or tval[0] == "Symptom" or tval[0] == "Behaviour":
            
                try:

                    t_idx_start = int(tval[1])
                    t_idx_end   = int(tval[2])

                    # WITH declared_found:
                    # Overall attribute accuracy:    0.2672
                    # Attribute accuracy
                    # Average per attribute type:
                    #     Status  Source
                    #     0.4768  0.3022


                    declared_found = find_declared_phrase(s_txt, t_idx_start, t_idx_end)
                    if declared_found:
                        y1 = ["Declared"]
                    else:
                        phrase = get_windowed_phrase(s_txt, t_idx_start, t_idx_end, 0, 0)
                        y1 = bc.predict([phrase])

                    #print("Phrase for " + str(tref) + ": [" + phrase + "]")
                    #print(str(y1))

                    if y1[0] == 'Declared': 
                        cnt_declared += 1
                        new_a_idx += 1
                        s = '\nA' + str(new_a_idx) + '\tSource T' + str(tref) + ' Declared'
                        
                        print(s.lstrip())
                        f_out.write(s)

                except (IndexError, ValueError) as e:

                    print('Error: ' + str(e) + ' - ' + str(tval))

        f_out.write("\n")
        f_out.close()  


    elif mode == "train": 
    # Głównie "pod., podejrzenie, podejrzeniem, w kierunku, w trakcie diagnostyki"

        #print('Preparing source on ' + filename + '...')

        fname, fext = os.path.splitext(filename)
        txt_filename = fname + '.txt'
        f_s = codecs.open(txt_filename, 'r', 'utf-8')
        s = f_s.read()
        f_s.close()

        f_out = codecs.open(filename, 'a+', 'utf-8')

        for t in annotations["T"].keys():

            v = ["", "", "", ""] # Dataset input vector + 1 field for significance

            tref = t
            tval = annotations["T"][tref].split()

            # v[0] is windowed phrase
            # v[1] is category
            # v[2] is ann filename
            # v[3] is tref

            v[0] = ""
            v[1] = "Confirmed"
            v[2] = filename
            v[3] = tref

            if tval[0] == "Investigation" or tval[0] == "Investigation_result" or tval[0] == "Drug" or tval[0] == "Drug_dose" or tval[0] == "Date" or tval[0] == "Treatment" or tval[0] == "Condition" or tval[0] == "Symptom" or tval[0] == "Behaviour":
                
                v[3] = tref

                try:

                    t_idx_start = int(tval[1])
                    t_idx_end   = int(tval[2])

                    phrase = get_windowed_phrase(s, t_idx_start, t_idx_end, 0, 0)

                    #print("Phrase for " + str(tref) + ": [" + phrase + "]")

                    v[0] = phrase

                    for a in annotations["A"].values():

                        asplit = a.split()
                        if asplit[1][1:] == tref and asplit[2] == "Declared":
                            #print('####################### Declared found in train: ' + v[0])
                            v[1] = "Declared"
                            break;

                    vs  = str(v[0]) + ';'
                    vs += str(v[1]) + ';'
                    vs += str(v[2]) + ';'
                    vs += str(v[3]) 

                    dataset_source_file.write(vs + '\n')

                except (IndexError, ValueError) as e:

                    n = 0

        f_out.close()


def _process_status_annotations(mode, filename, annotations, age, sex, rfc, bc, dataset_status_file_1, dataset_status_file_2, date_errors_file, date_bc):
    
    r_start, r_end = AgeSexImporter.extract_family_record(filename.split('.')[0] + '.txt')
               
    #print("Mode is " + mode)

    if mode == "annotate":

        print('Annotating status on ' + filename + '...')

        cnt_historical = 0
        cnt_family = 0

        f_dates = codecs.open(os.path.basename(filename) + ".dates", "w", "utf-8")

        s = ""


        # 0) Strip ending whitespaces (f.e.'/n') in the output filename

        try:
            f_out = codecs.open(filename, 'r', 'utf-8')
            s = f_out.read().rstrip()
            f_out.close()
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError in _process_status_annotations()")

        f_out = codecs.open(filename, 'w+', 'utf-8')
        f_out.write(s)
        
        max_a_idx = 0
        for a in annotations["A"].keys():
            try:
                if int(a) > max_a_idx:
                    max_a_idx = int(a)
            except ValueError:
                print('max_a_idx: ValueError in filename ' + filename + ': ' + str(a))

        #print('Max A idx for ' + filename + ' is ' + str(max_a_idx))

        new_a_idx = max_a_idx

        for t in annotations["T"].keys():
            tref = t
            tval = annotations["T"][tref].split()

            v = [sex, int(age), 0, 0, 0, 0, 0, 0, 0, 0, 0, ""] # Dataset input vector + 1 field for attribute       
            #v = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Less accurate results       

            #if tval[0] == "Treatment" or tval[0] == "Condition": #or tval[0] == "Symptom" or tval[0] == "Behaviour":
            if tval[0] == "Investigation" or tval[0] == "Investigation_result" or tval[0] == "Drug" or tval[0] == "Drug_dose" or tval[0] == "Date" or tval[0] == "Treatment" or tval[0] == "Condition" or tval[0] == "Symptom" or tval[0] == "Behaviour":
                
                v[10] = map_entity_type_to_code(tval[0])

                # 1) Find N ICD

                n_icd_found = False
                s_icd = ""
                for n in annotations["N"].values():
                    ref = n.split()[1][1:]
                    if ref == tref:
                        n_icd_found = True
                        s_icd = n.split()[2]
                        break

                if n_icd_found:
                    if len(s_icd) > 1:
                        icdcode = s_icd.split(':')[1] 
                        if len(icdcode) > 0:
                            v[2] = icdcode[0]
                            v[2] = ord(v[2]) - ord('A') + 1

                            if icdcode.find('.') > -1:
                                try:
                                    v[3] = int(icdcode.split('.')[0][1:])
                                    v[4] = int(icdcode.split('.')[1].replace('*', '')) #can ends with * or be f.e. K92..0
                                except ValueError:
                                    v[3] = 0
                                    v[4] = 0
                            else:
                                try:
                                    v[3] = int(icdcode[1:])
                                    v[4] = 0
                                except ValueError:
                                    v[3] = 0
                                    v[4] = 0

                # 2) Find T Date by R Dat
                
                s_date = ""
                t_date_found = False

                for r in annotations["R"].values():
                    rsplit = r.split()
                    if len(rsplit) > 2:

                        # T35 Behaviour 1699 1709 Nikotynizm
                        # T36 Date 1711 1717  40 lat
                        # R7  Dat Arg1:T36 Arg2:T35  

                        ref_0_nr = int(rsplit[2].split(':')[1][1:])                   
                        if (rsplit[0] == "Dat"):
                            if (ref_0_nr == int(tref)):

                                t_date_found = True

                                ref2 = rsplit[1].split(':')[1]
                                t_date = annotations["T"][ref2[1:]] #################
                                date0 = t_date.split()[3]   
                                d_1 = date.today()
                                s_date = " ".join(t_date.split()[3:][0:])
                                date_recognized, d_2, cform = calc_date(s_date, age, date_errors_file)
                                if date_recognized:
                                    try:
                                        d_2 = datetime.strptime(str(d_2.day) + "/" + str(d_2.month) + "/" + str(d_2.year), '%d/%m/%Y').date()
                                    except ValueError as e:
                                        print('_process_status_annotations(): strptime() error:' + str(e))
                                    v[5] = int((d_1 - d_2).days / 12)
                                    break
                                else:
                                    v[5] = 0

                                # todo: Canonical form for JSON

                                print('f_dates write: T' + str(tref) + " " + cform)
                                f_dates.write("T" + str(tref) + " " + cform + "\n")

                # 3) Check family record

                in_family_range = False
                if r_start > 0 and r_end > 0:
                    
                    try:  
                        r_text_start = int(annotations["T"][str(tref)].split()[1]) # was error - ref / tref
                        r_text_end = int(annotations["T"][str(tref)].split()[2])
                    except ValueError:
                        r_text_start = 0
                        r_text_end = 0

                    if r_start <= r_text_start and r_text_end <= r_end:
                        v[6] = r_start
                        v[7] = r_end
                        v[8] = r_text_start
                        v[9] = r_text_end

                        in_family_range = True

                        print('Family range for region (' + str(r_start) + ', ' + str(r_end) + ') is (' + str(r_text_start) + ', ' + str(r_text_end) + ')')

                # 4) Evaluate BC or RFC and annotate

                if in_family_range == True:
                     result = 2
                elif v[2]==0 and v[3]==0 and v[4]==0 and v[5]==0 and v[6]==0 and v[7]==0 and v[8]==0 and v[9]==0:
                    ts = " ".join(tval[3:])
                    result = int(bc.predict([ts])[0])
                    #print('Result of zero vector prediction for [' + ts + '] is ' + str(result))
                    if result > 0:
                        print("SIGNIFICANT RESULT for zero vector")
                # # Very bad results:
                # #elif s_icd == "ICD10:Z98.8":
                # #    result = 0
                elif t_date_found and not date_recognized:
                    print('Date predict: ' + s_date)
                    result = int(date_bc.predict([s_date])[0])
                    if result > 0:
                        print("SIGNIFICANT RESULT for unrecognized DATE pattern")
                else:                
####################### PONIŻEJ 2 METODY:
                    w = [v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10]]
                    result = rfc.predict([w])
                
                
                #ts = " ".join(tval[3:])
                #result = int(bc.predict([ts])[0])
                
                #print('Result for ' + str(v) + ' is ' + str(result))

                if result == 1: # Hist.Ins.
                ##############
                # Check bc because of redundant Historical - todo
                    #cnt_historical += 1
                    #ts = " ".join(tval[3:])
                    #result2 = int(bc.predict([ts])[0])
                    #if result2 > 0:
                    new_a_idx += 1
                    annotations['A'][str(new_a_idx)] = 'Status T' + str(tref) + ' Historical_Insignificant'
                    s = '\nA' + str(new_a_idx) + '\tStatus T' + str(tref) + ' Historical_Insignificant'
                    print(s.lstrip())
                    f_out.write(s)
                elif result == 2: # Family
                    #cnt_family += 1
                    new_a_idx += 1
                    annotations['A'][str(new_a_idx)] = 'Status T' + str(tref) + ' Family'
                    s = '\nA' + str(new_a_idx) + '\tStatus T' + str(tref) + ' Family'
                    print(s.lstrip())
                    f_out.write(s)

        f_out.write("\n")
        f_out.close()

        f_dates.close()

    elif mode == "train":

        ########################
        #   foreach n in annotations (N) which has reference to ICD
        #       find corresponding t 
        #       (treatment or condition, which will be annotated with significance) 
        #       and date using R Date and A Date

        # (basic, without main ilness)
        # Input vector: [Sex, Age, ICD_B_1, ICD_B_2, ICD_B_3, TimeSpan, FamilyRangeStart, FamilyRangeEnd, FamilyTextStart, FamilyTextEnd]

        #print('Preparing status on ' + filename + '...')

        key = os.path.splitext(filename)[0]
        txt_file_path = key + '.txt'
        f_txt = codecs.open(txt_file_path, 'r', 'utf-8')
        s_txt = f_txt.read().rstrip()
        f_txt.close()


        f_out = codecs.open(filename, 'r', 'utf-8')
        s = f_out.read().rstrip()
        f_out.close()
        
        # A) T without N ICD

        for tref in annotations["T"].keys():

            v = [sex, int(age), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, filename, 0, "", ""] # Dataset input vector + 1 field for significance
            #v = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, filename, 0] # Less accurate results 
                    
            v[10] = map_entity_type_to_code(annotations["T"][str(tref)].split()[0])
            
            v[12] = filename
            v[13] = tref

            add_vector = True # in each case! - was error -> False
            
            tval = annotations["T"][tref].split()                        
            if tval[0] == "Investigation" or tval[0] == "Investigation_result" or tval[0] == "Drug" or tval[0] == "Drug_dose" or tval[0] == "Date" or tval[0] == "Treatment" or tval[0] == "Condition" or tval[0] == "Symptom" or tval[0] == "Behaviour":
                
                #print(tval)

                try: # because of multiple ranges
                    v[14] = " ".join(tval[3:]) # todo --> ???: get_windowed_phrase(s, int(tval[1]), int(tval[2]))
                except ValueError as e:
                    print('Error: get_windowed_phrase() on compound range')

                associated_n_found = False
                for n in annotations["N"].values():
                    nref = n.split()[1][1:]
                    if tref == nref:
                        associated_n_found = True
                        break

                if not associated_n_found:

                    for a in annotations["A"].values():
                        try:
                            asplit = a.split()
                            if asplit[1][1:] == tref and asplit[2] == "Family":
                                if r_start > 0 and r_end > 0:
                                    try:
                                        r_text_start = int(annotations["T"][str(tref)].split()[1])
                                        r_text_end = int(annotations["T"][str(tref)].split()[2])
                                        v[6] = r_start
                                        v[7] = r_end
                                        v[8] = r_text_start
                                        v[9] = r_text_end
                                    except ValueError:
                                        v[8] = 0
                                        v[9] = 0

                                    v[11] = 2;
                                    add_vector = True
                                    break;

                            elif asplit[2] == "Declared":
                                continue

                            if asplit[1][1:] == tref and asplit[2] == "Historical_Insignificant":
                                #print('FOUND: Historical_Insignificant')
                                v[11] = 1
                                add_vector = True
                                #print('Input vector for Historical is ' + str(v))
                                break # ok
                            else:
                                v[11] = 0
                        except IndexError:
                            pass
                        #print (a)

                    s_date = ""
                    for r in annotations["R"].values():
                        rsplit = r.split()
                        if len(rsplit) > 2:
                            ref_0_nr = int(rsplit[2].split(':')[1][1:])                    
                            if (rsplit[0] == "Dat"):
                                if (ref_0_nr == int(tref)): # Error, was ref
                                    ref2 = rsplit[1].split(':')[1]

                                    t_date = annotations["T"][ref2[1:]]
                                    s_date = " ".join(t_date.split()[3:][0:])
                                    d_1 = datetime.today().date()
                                    date_recognized, d_2, cform = calc_date(s_date, age, date_errors_file)
                                    if date_recognized:
                                        v[5] = int((d_1 - d_2).days / 12)
                                    else:
                                        v[5] = 0

                                    v[15] = s_date
                                else:
                                    v[5] = 0

                    #print('Input vector = ' + str(v))

                    if v[2]==0 and v[3]==0 and v[4]==0 and v[5]==0 and v[6]==0 and v[7]==0 and v[8]==0 and v[9]==0 and v[11]>0:
                        print('Significant result for zero vector: ' + str(v[11]))

                    if add_vector == True:
                        s  = str(v[0]) + ';'
                        s += str(v[1]) + ';'
                        s += str(v[2]) + ';'
                        s += str(v[3]) + ';'
                        s += str(v[4]) + ';'
                        s += str(v[5]) + ';'
                        s += str(v[6]) + ';'
                        s += str(v[7]) + ';'
                        s += str(v[8]) + ';'
                        s += str(v[9]) + ';'
                        s += str(v[10]) + ';'
                        s += str(v[11]) + ';'
                        s += str(v[12]) + ';'
                        s += str(v[13]) + ';'
                        s += str(v[14]) + ';'
                        s += str(v[15])

                        #print("Write [" + str(s) + "]")

                        try:
                            dataset_status_file_1.write(s + '\n')
                        except UnicodeError as e:
                            print('UnicodeError on writing status')

        # B) T with N ICD
            
        words_r = 0
        words_l = 0

        for n in annotations["N"].values():

            ref = n.split()[1][1:]

            v = [sex, int(age), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, filename, 0, "", ""] # Dataset input vector + 1 field for significance
            #v = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, filename, 0] # Less accurate results 
                    
            v[10] = 0 # map_entity_type_to_code(annotations["T"][str(ref)].split()[0])
            
            #print ('REFERENCE = ' + str(ref))
            #print (n)
            icd = n.split()[2]
            #print('ICD code is ' + icd)
            #print (annotations["T"][ref])

            if len(icd) > 1:
                icdcode = icd.split(':')[1] 
                if len(icdcode) > 0:
                    v[2] = icdcode[0]
                    v[2] = ord(v[2]) - ord('A') + 1

                    if icdcode.find('.') > -1:
                        #print ('ICD: ' + icdcode)
                        try:
                            v[3] = int(icdcode.split('.')[0][1:])
                            v[4] = int(icdcode.split('.')[1].replace('*', '')) #can ends with * or be f.e. K92..0
                            #v[4] = 0 # todo
                        except ValueError:
                            v[3] = 0
                            v[4] = 0
                    else:
                        try:
                            v[3] = int(icdcode[1:])
                            v[4] = 0
                        except ValueError:
                            v[3] = 0
                            v[4] = 0

                    in_family_range = False
                    for a in annotations["A"].values():
                        try:
                            asplit = a.split()
                            if asplit[1][1:] == ref and asplit[2] == "Family":
                                if r_start > 0 and r_end > 0:
                                    v[6] = r_start
                                    v[7] = r_end
                                    try:
                                        r_text_start = int(annotations["T"][str(ref)].split()[1])
                                        r_text_end = int(annotations["T"][str(ref)].split()[2])
                                        v[8] = r_text_start
                                        v[9] = r_text_end
                                        in_family_range = True
                                    except ValueError:
                                        v[8] = 0
                                        v[9] = 0

                                    try:
                                        x_1 = int(annotations["T"][str(ref)].split()[1])
                                        x_2 = int(annotations["T"][str(ref)].split()[2])
                                        v[14] = get_windowed_phrase(s_txt, x_1, x_2, words_l, words_r)
                                        #print('x_1, x_2, v[14] = ' + str(x_1) + ', ' + str(x_2) + ', ' + v[14])
                                    except ValueError as e:
                                        print('Error: get_windowed_phrase() on compound range')


                                    v[11] = 2;
                                    #print('Input vector for Family is ' + str(v))
                                    break;

                            elif asplit[2] == "Declared":
                                continue

                            if asplit[1][1:] == ref and asplit[2] == "Historical_Insignificant":

                                try:
                                    s_1 = annotations["T"][str(ref)].split()[1]
                                    s_2 = annotations["T"][str(ref)].split()[2]
                                    #print('s_1, s_2 is ' + s_1 + ', ' + s_2)
                                    if ';' in s_2:
                                        s_2 = s_2.split(';')[0]
                                    x_1 = int(s_1)
                                    x_2 = int(s_2)
                                    v[14] = get_windowed_phrase(s_txt, x_1, x_2, words_l, words_r)
                                    #print('x_1, x_2, v[14] = ' + str(x_1) + ', ' + str(x_2) + ', ' + v[14])
                                except ValueError as e:
                                    print('Error: get_windowed_phrase() on compound range: ' + str(e))


                                v[11] = 1
                                #print('Input vector for Historical is ' + str(v))
                                break # ok

                            else:

                                try:
                                    s_1 = annotations["T"][str(ref)].split()[1]
                                    s_2 = annotations["T"][str(ref)].split()[2]
                                    #print('s_1, s_2 is ' + s_1 + ', ' + s_2)
                                    if ';' in s_2:
                                        s_2 = s_2.split(';')[0]
                                    x_1 = int(s_1)
                                    x_2 = int(s_2)
                                    v[14] = get_windowed_phrase(s_txt, x_1, x_2, words_l, words_r)
                                    #print('x_1, x_2, v[14] = ' + str(x_1) + ', ' + str(x_2) + ', ' + v[14])
                                except ValueError as e:
                                    print('Error: get_windowed_phrase() on compound range')

                                v[11] = 0
                        except IndexError:
                            v[8] = 0
                        #print (a)

    # T121    Treatment 5734 5776 zespoleniu systemowo-pĹ‚ucnym prawostronnym
    # N43 Reference T121 ICD10:Z98.8  Inne okreĹ›lone stany po zabiegach chirurgicznych
    # T122    Date 5778 5788  10.02.1994
    # T123    Treatment 5795 5819 korekcji caĹ‚kowitej wady
    # N44 Reference T123 ICD10:Z98.8  Inne okreĹ›lone stany po zabiegach chirurgicznych
    # T124    Date 5821 5831  01.02.1996
    # T125    Treatment 5842 5883 walwuloplastyce balonowej tÄ™tnicy pĹ‚ucnej
    # T126    Date 5885 5895  23.06.1999
    # T127    Condition 5898 5946 zwÄ™ĹĽenie i niedomykalnoĹ›Ä‡ zastawki pĹ‚ucnej I/II*
    # N45 Reference T127 ICD10:I37.2  ZwÄ™ĹĽenie zastawki pnia pĹ‚ucnego z niedomykalnoĹ›ciÄ…
    # R35 Dat Arg1:T122 Arg2:T121 
    # R36 Dat Arg1:T124 Arg2:T123 
    # R37 Dat Arg1:T126 Arg2:T125

                for r in annotations["R"].values():
                    rsplit = r.split()
                    if len(rsplit) > 2:
                        ref_0_nr = int(rsplit[2].split(':')[1][1:])                    
                        if (rsplit[0] == "Dat"):
                            if (ref_0_nr == int(ref)):
                                ref2 = rsplit[1].split(':')[1]

                                t_date = annotations["T"][ref2[1:]]
                                s_date = " ".join(t_date.split()[3:][0:])
                                d_1 = datetime.today().date()
                                date_recognized, d_2, cform = calc_date(s_date, age, date_errors_file)
                                if date_recognized:
                                    v[5] = int((d_1 - d_2).days / 12)
                                else:
                                    v[5] = 0

                                v[15] = s_date
                            else:
                                v[5] = 0

                # print('Input vector = ' + str(v))

                #if v[2]==0 and v[3]==0 and v[4]==0 and v[5]==0 and v[6]==0 and v[7]==0 and v[8]==0 and v[9]==0 and v[10]>0:
                #        print('Significant result for zero vector: ' + str(v[10]))

                s  = str(v[0]) + ';'
                s += str(v[1]) + ';'
                s += str(v[2]) + ';'
                s += str(v[3]) + ';'
                s += str(v[4]) + ';'
                s += str(v[5]) + ';'
                s += str(v[6]) + ';'
                s += str(v[7]) + ';'
                s += str(v[8]) + ';'
                s += str(v[9]) + ';'
                s += str(v[10]) + ';'
                s += str(v[11]) + ';'
                s += str(v[12]) + ';'
                s += str(v[13]) + ';'
                s += str(v[14]) + ';'
                s += str(v[15])

                try:
                    dataset_status_file_1.write(s + '\n')
                except UnicodeEncodeError as e:
                    print ('UnicodeEncodeError on dataset_status_file_1.write().')


def readannfile(mode, filename, age, sex, status_rfc, status_bc, source_bc, dataset_source_file, dataset_status_file_1, dataset_status_file_2, date_errors_file, date_bc):
    """
    Read an .ann file and returns a dictionary containing dictionaries.

    :param filename: (string) the filename of the .ann file.
    :return: (dict of dict) a dictionary of dictionaries representing the
    annotations.
    """
    anndict = defaultdict(dict)

    with open(filename, encoding='utf-8', errors='ignore') as f:
        try:
            for index, line in enumerate(f):

                begin = line.rstrip().split("\t")[0]
                rest = line.rstrip().split("\t")[1:]

                try:
                    anndict[begin[0]][begin[1:]] = u"\t".join(rest)
                except IndexError:
                    print('readannfile(): Index error')
                    continue
        except UnicodeDecodeError as e:
            print('UnicodeDecodeError in readannfile()')

    _process_status_annotations(mode, filename, anndict, age, sex, status_rfc, status_bc, dataset_status_file_1, dataset_status_file_2, date_errors_file, date_bc)
    _process_source_annotations(mode, filename, anndict, age, sex, source_bc, dataset_source_file)
