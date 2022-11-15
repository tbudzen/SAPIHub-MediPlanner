import codecs
import glob
import hashlib
import os
import shutil
import sys
import time

import spacy

from db_server import PIPELINE_WORK_CRF_FOLDER, PIPELINE_WORK_FOLDER
from nlp_pipeline.agreement.agreement import Agreement
from nlp_pipeline.attributes.attributes import Attributes
from nlp_pipeline.crf.conversion.myconversion import MyConversion
from nlp_pipeline.crf.deconversion.deconversion import Deconversion
from nlp_pipeline.evaluation.evaluation import Evaluation
from nlp_pipeline.evaluation.prepare import EvaluationPreparation
from nlp_pipeline.evaluation.prepare_baseline import EvaluationPreparationBaseline
from nlp_pipeline.json_exporter import JSONExporter
from nlp_pipeline.normalisation.basic.createDictionary import DictionaryCreation
from nlp_pipeline.normalisation.basic.normalise import Normalisation
from nlp_pipeline.relations.myrelations import MyRelations


##########################################################################################


class NLPPipeline():
    # Default directories and subdirectories

    default_work_dir = ""

    crf_dir = ""

    names_input_train_dir = ""
    names_input_process_dir = ""
    names_temp_features_train_dir = ""
    names_temp_features_process_dir = ""
    names_output_dir = ""

    attributes_input_train_dir = ""
    attributes_input_process_dir = ""
    attributes_output_dir = ""

    normalisation_input_dir = ""
    normalisation_output_dir = ""

    relations_input_dir = ""
    relations_output_dir = ""

    # Processor classes

    ev = None
    evp = None
    evpb = None
    attr = None
    ev = None
    agr = None
    mc = None
    mr = None
    dc = None
    norm = None
    deconv = None
    jsone = None

    def copy_src_dir_to_fresh_dir(self, from_dir, to_dir):

        if os.path.isdir(to_dir):
            shutil.rmtree(to_dir)

        shutil.copytree(from_dir, to_dir)

    def __init__(self, nlp):

        self.default_work_dir = "work"

        self.crf_dir = "crf"

        self.names_input_train_dir = "train"
        self.names_input_process_dir = "test"

        self.ev = Evaluation()
        self.evp = EvaluationPreparation()
        self.evpb = EvaluationPreparationBaseline()
        self.attr = Attributes()
        self.ev = Evaluation()
        self.agr = Agreement()
        self.mc = MyConversion(nlp)
        self.mr = MyRelations(nlp)
        self.dc = DictionaryCreation(nlp)
        self.norm = Normalisation(nlp)
        self.deconv = Deconversion()

        self.jsone = JSONExporter()

    ##########################################################################################

    def safe_delete_and_create_dir(self, dir):
        pass

    ##########################################################################################

    def prepare_evaluation(self):

        # 1.	Podział danych na porcję treningową i testową:
        # $ python3 prepare.py <WORKDIR>

        # 2.	Podział danych pochodzących od różnych znakujących:
        # $ python3 prepare-baseline.py <WORKDIR>

        # 3.	Obliczenie wewnętrznej zgodności między znakującymi:
        # $ python3 evaluation.py <WORKDIR>/gold <WORKDIR>/candidate baseline.tsv

        dir = os.getcwd()

        self.evp.prepare('work')

        self.evpb.prepare_baseline()

        self.ev.evaluate("work/gold", "work/candidate", "baseline.tsv")

        os.chdir(dir)

    ##########################################################################################

    def names_detection_train(self):  # CRF

        print('########################################################################')
        print('    Names detection training...')
        print('########################################################################')

        dir = os.getcwd()

        # 1.	Utworzenie katalogów tymczasowych: <TRAIN-FEATURES>, <TEST-FEATURES>, <TEST-OUTPUT>, <TEST-PRED>

        # 2.	Konwersja danych treningowych do plików z cechami:
        #	$ cd <KONWERSJA>
        # $ python3 myconversion.py <WORKDIR>/train <TRAIN_FEATURES> 1
        # $ python3 myconversion.py <WORKDIR>/test <TEST_FEATURES> 0

        print("cwd = " + os.getcwd())

        self.mc.my_conversion("work/train", "work/train_features", "1")
        self.mc.my_conversion("work/test", "work/test_features", "0")

        # 3.	Połączenie danych treningowych:
        #	$ cat <TRAIN_FEATURES>/*.crf > train.crf

        f_dest = codecs.open("work/train.crf", "w+", "utf-8")
        for path in glob.iglob("work/train_features/*.crf"):
            try:
                f = codecs.open(path, "r", "utf-8")
                f_s = f.read()
                f_dest.write(f_s)
                f.close()
            except Exception as e:
                print('Exception while creation of train.crf: ' + str(e))
                raise e
        f_dest.close()

        # 4.	Trenowanie modelu CRF:
        #	$ <CRF++>/bin/crf_learn temp3.t train.crf model.m

        print('########################################################################')
        print('    Learning CRF...')
        print('########################################################################')

        print("cwd = " + os.getcwd())  # Should be main nlp_pipeline directory here
        # os.chdir("work/crf")
        os.system("crf_learn work/temp3.t work/train.crf work/model.m")  # On Windows crf_learn should be in PATH

        os.chdir(dir)

    def names_detection_test(self):

        print('########################################################################')
        print('    Names detection testing...')
        print('########################################################################')

        # 5.	Zastosowanie modelu do danych testowych:
        # $ for FILE in <TEST_FEATURES>/*.crf; do <CRF++>/bin/crf_test -m model.m $FILE > <TEST_OUTPUT>/${FILE##*/}; done

        dir = os.getcwd()

        os.chdir(PIPELINE_WORK_CRF_FOLDER)

        if sys.platform == "win32":
            for path in glob.iglob("../test_features/*.crf"):
                os.system("../../crfpp/crf_test -m ../model.m " + path + " > ../test_output_names/" + os.path.basename(path))
        elif sys.platform == "linux":
            for path in glob.iglob("../test_features/*.crf"):
                os.system("crf_test -m ../model.m " + path + " > ../test_output_names/" + os.path.basename(path))

        # 6.	Konwersja rezultatu do formatu brat:
        # $ for FILE in <TEST_OUTPUT>/*.crf; do python3 deconversion.py $FILE <TEST_PRED>/$(basename -- "$FILE" .crf).ann; done

        for path in glob.iglob("../test_output_names/*.crf"):
            f_ann_name = os.path.basename(path).split(".")[0] + ".ann"
            self.deconv.deconversion(path, f_ann_name)

        # 7.	Ewaluacja na danych testowych:
        # $ python3 agreement.py <WORKDIR>/test <TEST_PRED> result.tsv

        os.chdir("..")
        self.agr.do_agreement("test", "test_output_names", "result_names.tsv")

        os.chdir(dir)

    def names_detection_process(self, bAgreement, guid):  # CRF

        print('########################################################################')
        print('    Names detection processing...')
        print('########################################################################')

        # 2.	Konwersja danych treningowych do plików z cechami:
        #	$ cd <KONWERSJA>
        # $ python3 myconversion.py <WORKDIR>/train <TRAIN_FEATURES> 1
        # $ python3 myconversion.py <WORKDIR>/test <TEST_FEATURES> 0

        # Copying for attributes AgeSexImporter

        # suffix to be used to force multithreading support
        suffix = "_" + guid

        # disabling suffix, too many implicit file paths pointing to files without suffixes
        suffix = ""

        for path in glob.iglob("work/test/*.txt"):
            shutil.copyfile(path, 'work/test_output_names' +suffix +'/' + os.path.basename(path))

        # self.mc.my_conversion("work/train", "work/train_features", "1")
        #
        # #3.	Połączenie danych treningowych:
        # #	$ cat <TRAIN_FEATURES>/*.crf > train.crf
        #
        # f_dest = open("work/train.crf", "w+")
        # for path in glob.iglob("work/train_features/*.crf"):
        #     try:
        #         f = open(path, "r")
        #         f_s = f.read()
        #         f_dest.write(f_s)
        #         f.close()
        #     except FileNotFoundError as e:
        #         print('File error: ' + str(e))
        # f_dest.close()
        #
        #

        self.mc.my_conversion("work/test", "work/test_features" + suffix, "0")

        # 5.	Zastosowanie modelu do danych testowych:
        # $ for FILE in <TEST_FEATURES>/*.crf; do <CRF++>/bin/crf_test -m model.m $FILE > <TEST_OUTPUT>/${FILE##*/}; done

        dir = os.getcwd()

        # WARNING: On Windows crf should be in PATH
        # os.chdir("work/crf")
        if sys.platform == "win32":
            for path in glob.iglob("work/test_features/*.crf"):
                print('Crf testing file ' + str(path))
                os.system("crf_test -m work/model3_2.m " + path + " > work/test_output_names/" + os.path.basename(path))
        elif sys.platform == "linux":
            for path in glob.iglob("work/test_features/*.crf"):
                print('Crf testing file ' + str(path))
                os.system("crf_test -m work/model3_2.m " + path + " > work/test_output_names/" + os.path.basename(path))

        # 6.	Konwersja rezultatu do formatu brat:
        # $ for FILE in <TEST_OUTPUT>/*.crf; do python3 deconversion.py $FILE <TEST_PRED>/$(basename -- "$FILE" .crf).ann; done

        for path in glob.iglob("work/test_output_names/*.crf"):
            print("Deconverting file " + path)
            f_ann_name = "work/test_output_names/" + os.path.basename(path).split(".")[0] + ".ann"
            self.deconv.deconversion(path, f_ann_name)

        # 7.	Ewaluacja na danych testowych:
        # $ python3 agreement.py <WORKDIR>/test <TEST_PRED> result.tsv

        if bAgreement:
            #TODO  ..!
            os.chdir("..")
            self.agr.do_agreement("test", "test_output_names", "result_names.tsv")

        os.chdir(dir)

    ##########################################################################################

    # 1.	Utworzenie katalogów tymczasowych: <TEST-INPUT>, <TEST-PRED>

    # 2.	Przygotowanie słownika nazw pojęć na podstawie danych treningowych:
    # $ python3 createDictionary.py <WORKDIR>/train dict.tsv

    # 3.	Usunięcie informacji o relacjach z danych testowych:
    # $ for FILE in <WORKDIR>/test/*.ann; do cat $FILE | grep -v -P '^N[0-9]+\t' > <TEST-INPUT>/$(basename -- "$FILE"); done
    # $ cp <WORKDIR>/test/*.txt <TEST-INPUT>

    # 4.	Automatyczne odgadnięcie normalizacji w danych testowych na podstawie słownika:
    # $ python3 ./normalise.py <TEST-INPUT> <TEST-PRED> dict.tsv

    # 5.	Ewaluacja na danych testowych:
    # $ python3 agreement.py <WORKDIR>/test <TEST_PRED> result.tsv

    def normalisation_train(self):

        print('########################################################################')
        print('    Normalisation training...')
        print('########################################################################')

        dir = os.getcwd()

        self.dc.dictionary_create("work/original_to_evaluate", "work/dict.tsv")

        os.chdir(dir)

    def normalisation_test(self):

        print('########################################################################')
        print('    Normalisation testing...')
        print('########################################################################')

        dir = os.getcwd()

        shutil.rmtree("work/test_input")

        shutil.copytree("work/test", "work/test_input")

        self.attr.strip_annotations("work/test_input", "N")

        self.norm.normalise("test_input", "test_pred", "work/dict.tsv")
        self.agr.do_agreement("test", "test_pred", "result_normalisation.tsv")

        os.chdir(dir)

    def normalisation_process(self, bAgreement, guid):

        print('########################################################################')
        print('    Normalisation processing...')
        print('########################################################################')

        # os.system("for FILE in " + work_dir + "/test/*.ann; do cat $FILE | grep -v -P '^N[0-9]+\\t' > " +
        #          test_input_dir + "/$(basename -- \"$FILE\"); done")

        # os.system("cp " + work_dir + "/test/*.txt " + test_input_dir)

        dir = os.getcwd()

        if os.path.isdir("work/test_input_normalisation"):
            shutil.rmtree("work/test_input_normalisation")

        gl = glob.iglob("work/test_output_names/*.ann")
        for path in gl:
            shutil.copyfile(path, 'work/test_output_normalisation/' + os.path.basename(path))

        gl = glob.iglob("work/test_output_names/*.txt")
        for path in gl:
            shutil.copyfile(path, 'work/test_output_normalisation/' + os.path.basename(path))

        # shutil.copytree("work/test", "work/test_input_normalisation")
        shutil.copytree("work/test_output_names", "work/test_input_normalisation")

        self.attr.strip_annotations("work/test_input_normalisation", "N")

        self.norm.normalise("test_input_normalisation", "test_output_normalisation", "dict.tsv")

        if bAgreement:
            self.ev.evaluate("test", "test_output_normalisation", "result_normalisation.tsv")
            # self.agr.do_agreement("test", "test_output_normalisation", "result_normalisation.tsv")

        os.chdir(dir)

    ##########################################################################################

    # 1.	Utworzenie katalogów tymczasowych: <TEST-INPUT>, <TEST-PRED>

    # 2.	Usunięcie informacji o relacjach z danych testowych:
    # $ for FILE in <WORKDIR>/test/*.ann; do cat $FILE | grep -v -P '^R[0-9]+\t' > <TEST-INPUT>/$(basename -- "$FILE"); done
    # $ cp <WORKDIR>/test/*.txt <TEST-INPUT>

    # 3.	Wykonanie skryptu wykrywającego relacje:
    # $ python3 myrelations.py <TEST-INPUT> <TEST_PRED>

    # 4.	Ewaluacja na danych testowych:
    # $ python3 agreement.py <WORKDIR>/test <TEST_PRED> result.tsv

    def relations_train(self):

        print('########################################################################')
        print('    Relations training...')
        print('########################################################################')

        dir = os.getcwd()

        # os.chdir("work")
        #
        # shutil.rmtree("test_input_relations")
        # shutil.copytree("test", "test_input_relations")
        #
        # self.attr.strip_annotations("test_input_relations", "R")
        #
        # self.mr.process_relations("test_input_relations", "test_pred_relations")
        #
        # self.agr.do_agreement("test", "test_pred_relations", "result_relations.tsv")

        os.chdir(dir)

    def relations_test(self):

        print('########################################################################')
        print('    Relations testing...')
        print('########################################################################')

        dir = os.getcwd()

        os.chdir(PIPELINE_WORK_FOLDER)

        self.mr.process_relations("test_input", "test_pred")

        self.agr.do_agreement("test", "test_pred", "result_relations.tsv")

        os.chdir(dir)

    def relations_process(self, bAgreement, guid):

        print('########################################################################')
        print('    Relations processing...')
        print('########################################################################')

        dir = os.getcwd()

        os.chdir(PIPELINE_WORK_FOLDER)

        for path in glob.iglob("test_output_normalisation/*.*"):
            shutil.copyfile(path, 'test_input_relations/' + os.path.basename(path))

        for path in glob.iglob("test_output_normalisation/*.txt"):
            shutil.copyfile(path, 'test_output_relations/' + os.path.basename(path))

        self.attr.strip_annotations("test_input_relations", "R")

        self.mr.process_relations("test_input_relations", "test_output_relations")

        if bAgreement:
            self.agr.do_agreement("test", "test_output_relations", "result_relations.tsv")

        os.chdir(dir)

    ##########################################################################################

    def attributes_train(self):

        print('########################################################################')
        print('    Attributes training...')
        print('########################################################################')

        dir = os.getcwd()

        os.chdir(PIPELINE_WORK_FOLDER)

        self.attr.create_datasets('train', "dataset_in_source.txt", "dataset_in_status_1.txt",
                                  "dataset_in_status_2.txt")
        self.attr.train_status("dataset_in_status_1.txt", "dataset_in_status_1.txt", "status_rfc.sav",
                               "status_bc.sav", "status_bc_date.sav")
        self.attr.train_source("dataset_in_source.txt", "source_bc.sav")

        os.chdir(dir)

    def attributes_test(self):

        print('########################################################################')
        print('    Attributes testing...')
        print('########################################################################')

        dir = os.getcwd()

        self.attr.strip_annotations('work/test', 'A')
        self.attr.annotate('work/test', 'work/status_rfc.sav',
                           'work/status_bc.sav', 'work/status_bc_date.sav', 'work/source_bc.sav',
                           "dataset_test_source.txt",
                           "dataset_test_status_1.txt", "dataset_test_status_2.txt")

        self.ev.evaluate("test_output_attributes", "test", "result_attributes.tsv")

        os.chdir(dir)

    def attributes_process(self, bAgreement, guid):

        print('########################################################################')
        print('    Attributes processing...')
        print('########################################################################')
        #
        dir = os.getcwd()

        # for path in glob.iglob("work/test_output_names/*.*"):
        for path in glob.iglob("work/test_output_relations/*.*"):
            shutil.copyfile(path, 'work/test_output_attributes/' + os.path.basename(path))

        self.attr.strip_annotations('work/test_output_attributes', 'A')
        print("cwd = " + os.getcwd())
        # os.chdir('test_output_attributes')
        self.attr.annotate('test_output_attributes', "status_rfc.sav", "status_bc.sav",
                           "status_bc_date.sav", "source_bc.sav",
                           "dataset_test_source.txt",
                           "dataset_test_status_1.txt", "dataset_test_status_2.txt")

        # os.chdir(dir)

        for path in glob.iglob("work/test_output_attributes/*.ann"):
            basef = os.path.basename(path).split('.')[0]
            self.jsone.convert(path, basef + ".txt", basef + ".json")

        if bAgreement:
            print("evaluate cwd = " + os.getcwd())
            self.ev.evaluate("test", "test_output_attributes", "result_attributes.tsv")

        os.chdir(dir)

    ##########################################################################################

    def rm_and_create_dir(self, dir):

        if os.path.isdir(dir):
            shutil.rmtree(dir)

        os.mkdir(dir)

    def prepare_dirs(self, guid):

        dir = os.getcwd()

        os.chdir(PIPELINE_WORK_FOLDER)

        # O M G .....

        # suffix to be used to force multithreading support
        suffix = "_" + guid

        # disabling suffix, too many implicit file paths pointing to files without suffixes
        suffix = ""
        self.rm_and_create_dir("test_features"+suffix)
        self.rm_and_create_dir("test_input_attributes"+suffix)
        self.rm_and_create_dir("test_input_normalisation"+suffix)
        self.rm_and_create_dir("test_input_relations"+suffix)
        self.rm_and_create_dir("test_output_attributes"+suffix)
        self.rm_and_create_dir("test_output_names"+suffix)
        self.rm_and_create_dir("test_output_normalisation"+suffix)
        self.rm_and_create_dir("test_output_relations"+suffix)
        self.rm_and_create_dir("test_pred"+suffix)
        self.rm_and_create_dir("test_pred_relation"+suffix)
        self.rm_and_create_dir("train_features"+suffix)

        # Needed for dict.tsv
        # self.rm_and_create_dir("train")

        os.chdir(dir)

    def preparation(self):

        self.prepare_evaluation()

    def train(self, submode):

        if submode == "names":
            self.names_detection_train()

        elif submode == "attributes":
            self.attributes_train()

        elif submode == "normalisation":
            self.normalisation_train()

        elif submode == "relations":
            self.relations_train()

        elif submode == "all":

            time_1 = time.time()

            self.names_detection_train()
            self.normalisation_train()
            self.relations_train()
            self.attributes_train()

            time_2 = time.time()

            t_delta = (time_2 - time_1)

            print("Total time = " + str(t_delta) + " [s]")

    def test(self, submode):

        if submode == "names":
            self.names_detection_test()

        elif submode == "attributes":
            self.attributes_test()

        elif submode == "normalisation":
            self.normalisation_test()

        elif submode == "relations":
            self.relations_test()

        elif submode == "all":
            self.names_detection_test()
            self.normalisation_test()
            self.relations_test()
            self.attributes_test()

    def process(self, submode, bAgreement, guid):

        if submode == "names":  # CRF
            self.names_detection_process(bAgreement, guid)

        elif submode == "attributes":
            self.attributes_process(bAgreement, guid)

        elif submode == "normalisation":
            self.normalisation_process(bAgreement, guid)

        elif submode == "relations":
            self.relations_process(bAgreement, guid)

        elif submode == "all":

            self.prepare_dirs(guid)

            time_0 = time.time()

            self.names_detection_process(bAgreement, guid)

            time_1 = time.time()

            self.normalisation_process(bAgreement, guid)

            time_2 = time.time()

            self.relations_process(bAgreement, guid)

            time_3 = time.time()

            self.attributes_process(bAgreement, guid)

            time_4 = time.time()

            t_delta = time_4 - time_0

            print("Time of name detection  = " + str(time_1 - time_0) + " [s]")
            print("Time of normalisation   = " + str(time_2 - time_1) + " [s]")
            print("Time of relations       = " + str(time_3 - time_2) + " [s]")
            print("Time of attributes      = " + str(time_4 - time_3) + " [s]")

            print("Total time = " + str(t_delta) + " [s]")

    def process_text(self, text, bAgreement, guid):

        #files = glob.glob('work/test/*')
        #for f in files:
        #    os.remove(f)

        path = "work/test/tmp_input_" + guid + ".txt"

        # disabling suffix, too many implicit file refs in this code...
        path = "work/test/tmp_input.txt"

        # comment from PIOTR: please refactor the code to use unique filenames per request:, like so
        #  path = "work/test/" + hashlib.sha384(str.encode(text)).hexdigest() + ".txt"
        # and add redundant file deletion step on finished processing

        #print("CWD = " + os.getcwd())

        #print("process_text -> " + text)

        f = open(path, "w", encoding="utf-8")
        f.write(text)
        f.close()

        self.process_file(path, False, bAgreement, guid)

    def process_file(self, filepath, withcopy, bAgreement, guid):

        if withcopy:
            # will overwrite if dest exists
            shutil.copyfile(filepath, "work/test/" + os.path.basename(filepath))

        self.process("all", bAgreement, guid)


##########################################################################################

# Directories:
# work_dir (global, base)
# input_dir for evaluation preparation phase
# train -> train phase
# input_dir, output_dir -> process phase
# test, orig -> test phase


if __name__ == "__main__":
    cnt = len(sys.argv)
    if cnt >= 2:
        mode = sys.argv[1]
        submode = ""
        print("Loading pl_spacy_model...")
        nlp = spacy.load('pl_spacy_model')
        print("pl_spacy_model loaded.")
        pl = NLPPipeline(nlp)
        if mode == "prepare":
            pl.preparation()
        elif mode == "train":
            if cnt >= 3:
                submode = sys.argv[2]
                pl.train(submode)
            else:
                print("Error: Missing submode")
        elif mode == "test":
            if cnt >= 3:
                submode = sys.argv[2]
                pl.test(submode)
            else:
                print("Error: Missing submode")
        elif mode == "process":  # Directory
            if cnt >= 3:
                submode = sys.argv[2]
                pl.process(submode)  # Total time = 1656.5010430812836 [s]

            else:
                print("Error: Missing submode")
        elif mode == "processText":
            if cnt >= 3:
                text = sys.argv[2]
                pl.process_text(text, "")
            else:
                print("Error: Missing input text")
        elif mode == "processFile":
            if cnt >= 3:
                filename = sys.argv[2]
                pl.process_file(filename, True)
            else:
                print("Error: Missing input filename")
        else:
            print("Error: Incorrect mode: [" + mode + "]")
    else:
        print("Error: Missing mode")

    # Structure:
    # <work_dir>
    #   <train_dir>
    #   <input_dir>
    #   ... other temp. dirs
    #   <output_dir>
