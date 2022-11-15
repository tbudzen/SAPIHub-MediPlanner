import sys


class Deconversion():

    def deconversion(self, inputStr) -> str:

        print(" Deconversion crf ->ann ")
        currentCategory = None
        currentStart = None
        currentEnd = None
        currentString = None
        counter = 1
        counterT = 1
        out = ""
        try:

            lines = inputStr.splitlines()
            for line in lines:
                parts = line.split("\t")
                tag = parts[-1].strip()
                if len(parts) == 1:
                    continue
                if tag == "o":
                    if not currentCategory is None:
                        try:
                            out += ("T" + str(counterT) + "\t" + currentCategory + " " + str(currentStart) + " " + str(currentEnd) + "\t" + currentString + "\n")
                        except UnicodeEncodeError as e:
                            print("UnicodeEncodeError: " + str(e))
                        counterT = counterT + 1
                        currentCategory = None
                elif tag.startswith("b-"):
                    if not currentCategory is None:
                        try:
                            out += ("T" + str(counterT) + "\t" + currentCategory + " " + str(currentStart) + " " + str(currentEnd) + "\t" + currentString + "\n")
                        except UnicodeEncodeError as e:
                            print("UnicodeEncodeError: " + str(e))
                        counterT = counterT + 1
                    currentCategory = tag[2:]
                    currentStart = int(parts[-3])
                    currentEnd = currentStart + int(parts[-2])
                    currentString = parts[0]
                elif tag.startswith("i-"):
                    thisCategory = tag[2:]
                    if currentCategory is None or currentCategory != thisCategory:
                        print("Unexpected tag: " + tag + " in line " + str(counter))
                        if not currentCategory is None:
                            try:
                                out += ("T" + str(counterT) + "\t" + currentCategory + " " + str(currentStart) + " " + str(currentEnd) + "\t" + currentString + "\n")
                            except UnicodeEncodeError as e:
                                print("UnicodeEncodeError: " + str(e))
                            counterT = counterT + 1
                        currentCategory = tag[2:]
                        currentStart = int(parts[-3])
                        currentEnd = currentStart + int(parts[-2])
                        currentString = parts[0]
                    else:
                        thisStart = int(parts[-3])
                        if currentEnd != thisStart:
                            currentString = currentString + " "
                        currentString = currentString + parts[0]
                        currentEnd = thisStart + int(parts[-2])

                else:
                    print("Unexpected line: " + line)
                    sys.exit(-1)
                counter = counter + 1
        except UnicodeDecodeError as e:
            print('UnicodeDecodeError: ' + str(e))
        return out
