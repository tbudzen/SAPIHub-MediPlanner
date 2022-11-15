import sys
import pickle
import os

from glob import iglob

from actually_working_nlp_processor.attributes.annotation_processor import readannfile
from nlp_pipeline.attributes.age_sex_importer import AgeSexImporter
from nlp_pipeline.attributes.annotation_processor import processann



class AnnProcessor(object):
    """
    A class for modeling a local repository annotated with BRAT.

    Corpora annotated with Brat use 2 files for each document in the corpus:
    an .ann file containing the annotations in Brat Standoff Format
    (http://brat.nlplab.org/standoff.html), and a .txt file containing the
    actual text. This tool takes a folder containing pairs of these files as
    input, and creates a RepoModel object. This RepoModel object can be
    exported in an XML format, or operated on in memory.

    Currently the program ignores Notes, or # annotations.
    """

    def __init__(self, status_rfc_filename, status_bc_filename, status_bc_date_filename, source_bc_filename):
        """
        Create a RepoModel object.

        :param pathtorepo: (string) the path to a local repository, which
        contains pairs of .ann and .txt files. No checking is done to guarantee
        that the repository is consistent.
        :return: None
        """


        print("Loading classifiers for status and source...")

        self.status_rfc = pickle.load(open(status_rfc_filename, 'rb'))
        self.status_bc = pickle.load(open(status_bc_filename, 'rb'))
        self.status_bc_date = pickle.load(open(status_bc_date_filename, 'rb'))
        self.source_bc = pickle.load(open(source_bc_filename, 'rb'))

        print("Classifiers loaded.")

        # if not self.dataset_source_file is None: self.dataset_source_file.close()
        # if not self.dataset_status_file_1 is None: self.dataset_status_file_1.close()
        # if not self.dataset_status_file_2 is None: self.dataset_status_file_2.close()

    def annotate(self, text, relations, age, sex) -> str:
        # Each document is saved as a textunit.
        self.documents = {}
        try:
           return readannfile(text, relations, age, sex, self.status_rfc, self.status_bc, self.source_bc, self.status_bc_date)
        except KeyError as e:
            print("Parse error for document: {}, {} \n".format(str(e), sys.exc_info()[0]))

        return ""
