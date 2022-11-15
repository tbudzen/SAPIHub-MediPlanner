dbExtendedDataMap = {
    "cisnienie_skurczowe": "systole",
    "cisnienie_rozkurczowe": "diastole",
   # "wiek": "wiek",
    "plec": "gender",

}
dbPatientDataMap = {
    "wiek": "age",
}

textDataRegexMap = {
    "cholesterol_calkowity": {"regex": "C[hH][oO][lL][esterol ]{0,8}[całkowity ]{0,10}[: ]{0,5}(\d{1,3}[,.]{0,1}\d{0,2})[\[ ]{0,2}mg[\/]{0,1}dl", "type": "simple"},
    "cisnienie_skurczowe": {"regex": ["Ci.nienie [a-zśę ]{0,10}(\d{2,3})[\/ na]{1,4}\d{2,3}[ ]{0,2}mm.{0,1}[hH]g",  "(\d{2,3})[\/ na]{1,4}\d{2,3}[ ]{0,2}mm.{0,1}[hH]g"], "type": "simple"},
    "cisnienie_rozkurczowe": {"regex": ["Ci.nienie [a-zśę ]{0,10}\d{2,3}[\/ na]{1,4}(\d{2,3})[ ]{0,2}mm.{0,1}[hH]g",  "\d{2,3}[\/ na]{1,4}(\d{2,3})[ ]{0,2}mm.{0,1}[hH]g"], "type": "simple"},

    "LDL": {"regex": "(?:LDL|Llipoproteina niskiej gęstości)[^\d]*(\d{1,3}[,.]{0,1}\d{0,3})[^\d]", "type": "simple"},
    "HDL": {"regex": "HDL[^\d]*(\d{1,3}[,.]{0,1}\d{0,3})[^\d]", "type": "simple"},
   # "aktywnosc_fizyczna  h/tydz": {"regex": "ktywność fizyczna ([0-9,. ]+) h/tydz", "type": "simple"},
    "aktywnosc_fizyczna": {"regex": "ktywność fizyczna ([0-9,. ]+) h/tydz", "type": "simple"},
    "klasa_nadcisn": {"regex": " ([0-9IVX]+) klasa wg CCS", "type": "simple"}, # to be revisited
    "eGFR": {"regex": "eGFR[0-9a-zA-Z,.]{0,50}[: ]{0,5}([0-9,. ]+)[\[\(]{0,1}ml.{0,1}min", "type": "simple"},
    "D-dimery": {"regex": "[Dd]-dimery[0-9a-zA-Z,.]{0,50}[: ]{0,5}([0-9,. ]+)[\[\(]{0,1}μg/L", "type": "simple"},

  #  "ChSN": {"regex": "[Cc]horoby sercowo-naczyniowe", "type": "exists"},  # to be revisited
  #  "palenie": {"regex": "Palenie tytoniu: tak", "type": "exists"},
}

annotationAdditionalMap = {
    "cukrzyca": {"subtype": "Condition", "type": "T", "valueRegex": "cukrzyca", "entryType": "exists"},
}

synonymsMap = { #to be reviewed
    "powiklania_narzadowe": {"valueRegex": ".*powikłania narządowe.*", "entryType": "exists"},
    "zaburzenia_lipidowe": {"valueRegex": ".*zaburzenia lipidowe.*", "entryType": "exists"},
    "CKD": {"valueRegex": ".*przewlekła choroba nerek.*", "entryType": "exists"},
    "CAD": {"valueRegex": ".*choroba wieńcowa.*", "entryType": "exists"},
    "ciaza": {"valueRegex": ".* ciąża .*", "entryType": "exists"},
    "nadcis_przer_lkomory": {"valueRegex": ".*nadciśnieniowy przerost mięśnia lewej komory.*", "entryType": "exists"},
    "rewaskularyzacja_wiencowa_lub_inna": {"valueRegex": ".*rewaskularyzacja tętnicy.*", "entryType": "exists"},
    "choroba_tetnic_obwodowych": {"valueRegex": ".*choroba tętnic obwodowych.*", "entryType": "exists"},
    "tetniak_aorty": {"valueRegex": ".*tętniak aorty.*", "entryType": "exists"},
    "udar": {"valueRegex": ".*udar.*", "entryType": "exists"},
    "deprywacja": {"valueRegex": ".*deprywacja.*", "entryType": "exists"},
    "otylosc": {"valueRegex": ".*otylosc.*", "entryType": "exists"},
    "stres": {"valueRegex": ".*stres.*", "entryType": "exists"},
    "rodzinne_CVD": {"valueRegex": ".*CVD w rodzinie.*", "entryType": "exists"},
    "CVD": {"valueRegex": ".*CVD.*", "entryType": "exists"},
    "HMOD": {"valueRegex": ".*HMOD.*", "entryType": "exists"},
    "ABPM": {"valueRegex": ".*ABPM.*", "entryType": "exists"},
    "HFrEF": {"valueRegex": ".*HFrEF.*", "entryType": "exists"},
    "choroba_psychiczna": {"valueRegex": ".*choroba psychiczna.*", "entryType": "exists"},
    "HIV": {"valueRegex": ".*HIV.*", "entryType": "exists"},
    "migotanie_przedsionkow": {"valueRegex": ".*migotanie przedsionków.*", "entryType": "exists"},
    "przerost_lewej_komory": {"valueRegex": ".*przerost lewej komory.*", "entryType": "exists"},
    "bezdech": {"valueRegex": ".*bezdech.*", "entryType": "exists"},
    "choroba_autoimmunologiczna": {"valueRegex": ".*choroba autoimmunologiczna.*", "entryType": "exists"},
    "choroba_nerek": {"valueRegex": ".*choroba nerek.*", "entryType": "exists"},
    "choroba_wiencowa": {"valueRegex": ".*choroba wiencowa.*", "entryType": "exists"},
    "zespol_kruchosci": {"valueRegex": ".*zespół kruchości.*", "entryType": "exists"},
    "aktywnosc_fizyczna  h/tydz": {"valueRegex": ".*aktywnosc_fizyczna  h/tydz.*", "entryType": "exists"}, # to be removed
    "klasa_nadcisn": {"valueRegex": ".*aktywnosc_fizyczna  h/tydz.*", "entryType": "exists"}, # to be removed

}
