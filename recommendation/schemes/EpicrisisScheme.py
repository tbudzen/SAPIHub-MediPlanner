class EpicrisisScheme(object):

    def __init__(self) -> None:
        pass

    def generate(self, sex, age=None, glowne_objawy_wywiad=None, glowne_odchylenie_od_normy_przedmiotowy=None, abnormalResults=None, prescribedDrugs=None, lastTreatmentPlan=None) -> str:
        patient = "Pacjentka" if sex == "1" else "Pacjent"
        ya = "a" if sex == "1" else "y"
        return """<p>""" + patient + """ &nbsp;lat """ + str(int(age)) + """ <b> przyjęt""" + ya + """ do Kliniki z powodu </b> \n""" + glowne_objawy_wywiad + """</p>
           <p> <b> Podczas badania przedmiotowego zwraca uwagę na: </b></p> """ + glowne_odchylenie_od_normy_przedmiotowy + """ \n </p>
           <p> W EKG przy przyjęciu <b><i> [opis EKG]</i></b>.&nbsp;</p>
           <p> W ECHO <b><i>[wnioski z badania echokardiograficznego]</i></b>.&nbsp;</p>
           <p> Wykonana pr&oacute;ba dobutaminowa/wysiłkowa <b><i>[ujemna/dodatnia (tylko pr&oacute;ba dobutaminowa)]</i></b> echokardiograficznie, [ujemna/dodatnia] &nbsp;elektrokardiograficznie i [ujemna/dodatnia] klinicznie.&nbsp;</p>
           <p> W Holter-RR <b><i> [wnioski badania Holter-RR]</i></b>.&nbsp;</p>
           <p> W Holter-EKG <b><i> [wnioski badania Holter-EKG wraz z średnią częstością rytmu serca]</i></b>.&nbsp;</p>
           <p> W ergospirometrii <b><i> [opis badania]</i></b>.&nbsp;</p>
           <p> W badaniach laboratoryjnych:</p><p> """ + abnormalResults + """</p>
           <p> W USG <b><i>[narząd - opis USG (powt&oacute;rzyć z każdym wynikiem USG)]</i></b>.&nbsp;</p>
           <p> W RTG <b><i> [narząd - opis badania]</i></b>.&nbsp;</p>
           <p> W TK lub RM <b><i>[narząd - opis badania]</i></b>.&nbsp;</p>
           <p> Chor""" + ya + """  konsultowan""" + ya + """  przez <b><i> [adekwatny specjalista]</i></b>, zalecenia wdrożono.&nbsp;</p>
           <p> LUB Chor""" + ya + """  zakwalifikowan""" + ya + """  do zabiegu &hellip;&hellip;&hellip;&hellip;&hellip;..., kt&oacute;ry został wykonany w dn. &hellip;...&nbsp;</p>
           <p> Przebieg zabiegu powikłany/bez powikłań.&nbsp;</p>
           <p> Zmodyfikowano/kontynuowano farmakoterapię - """ + prescribedDrugs + """.&nbsp;</p>
            <p>  """ + patient + """ wypisan""" + ya + """  w stanie og&oacute;lnym <b><i>[złym/średnim/dobrym]</i></b> z zaleceniami jak poniżej
             i dalszej opieki w POZ i Poradni Kardiologicznej oraz <b><i>[Poradnie wg chor&oacute;b]</i></b>.</p>
            <p>  """ + lastTreatmentPlan + """.&nbsp;</p>
          
            """
