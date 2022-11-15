import codecs
import io
import os


class AgeSexImporter:

    def extract_family_record(txt_file_path):

        f = codecs.open(txt_file_path, 'r', 'utf-8')
        s = ""
        try:
            s = f.read()
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError in extract_age_sex_from_file(): " + str(e))
        s = s.lower()
        f.close()

        family_region_start = 0
        family_region_end = 0

        neg_l = ['nieistot', 'nie istot', 'nie podaj', 'bez znacz', 'b/z', 'negatywny', 'brak']

        neg_distance = 30

        stop_l = ['W dn.', 'Wykonano u pacjenta', 'Neguje', 'Choroby zakaźne', 'Przyjmowane obecnie leki', 'W wywiadzie ponadto', 'Palenie', 'Chroroby', 'Zabiegi', 'Przebyte', 'Inne', 'Nikotyn', 'Papieros', 'Alkohol', 'Leki', 'Leków', 'Uczuleni', 'Alergi', 'Stan spo', 'Status spo', '-----']  # wg ważności

        pos = s.find('wywiad rodzin')  # rodzinny, rodzinne, rodzina, w wywiadzie rodzinnym itp.
        if (pos == -1):
            pos = s.find('w wywiadzie rodzin')
        # print('Pos is ' + str(pos))

        if pos > 0:
            # print('Family region found at ' + str(pos))
            neg_found = False
            for neg_l_elem in neg_l:
                pos_neg = s.find(neg_l_elem, pos)
                if pos_neg > pos and pos_neg - pos < neg_distance:
                    neg_found = True
                    # print('Neg in family found at ' + str(pos_neg))
                    break;

            pos_stop_min = 100000
            pos_stop_min_elem = ""
            if pos > -1 and not neg_found:
                family_region_start = pos
                family_region_end = pos
                ## todo: minimum of stop_l_elem which is greater than pos
                for stop_l_elem in stop_l:
                    pos_stop = s.find(stop_l_elem.lower(), pos)
                    if -1 < pos_stop and pos_stop < pos_stop_min:
                        pos_stop_min = pos_stop
                        pos_stop_min_elem = stop_l_elem

                # print('pos, pos_stop_min is ' + str(pos) + ', ' + str(pos_stop_min) + ' for ' + pos_stop_min_elem)

                if pos_stop_min > pos and pos_stop_min < 100000:
                    # print('Pos stop found at ' + str(pos_stop) + ' for ' + stop_l_elem)
                    family_region_end = pos_stop_min

        # sr = s[family_region_start:family_region_end].rstrip()
        # if sr != "": print('Family region text is [' + sr + "]")

        return (family_region_start, family_region_end)

    def extract_age_sex_from_file(txt_file_path):

        # ------------------------------------------------
        # Wiek: 26 lat
        # ------------------------------------------------
        # ------------------------------------------------
        # PĹ‚eÄ‡: ĹĽeĹ„ska
        # ------------------------------------------------

        txtfile = codecs.open(txt_file_path, 'r', 'utf-8')
        lines = []
        try:
            lines = txtfile.readlines()
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError in extract_age_sex_from_file(): " + str(e))
        txtfile.close()

        print("LINES = " + str(lines))

        if len(lines) >= 5:
            age_line = lines[1].strip()
            if not age_line == "":
                print("age_line = " + age_line)
                try:
                    age = age_line.split()[1]
                except:
                    age = 35
            else:
                age = 35

            sex_line = lines[4]
            if not sex_line == "":
                sex_text = sex_line.split()[1]
                if (sex_text == "żeńska"):
                    sex = -1
                elif (sex_text == "męska"):
                    sex = 1
                else:
                    sex = 0  # unknown
            else:
                sex = -1
        else:
            sex = -1
            age = 35

        return (age, sex)
