import sys
import pickle
import os

from glob import iglob

from age_sex_importer import AgeSexImporter
from annotation_processor import processann



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

    def __init__(self, mode, ann_dir, status_rfc_filename, status_bc_filename, status_bc_date_filename, source_bc_filename, dataset_source_filename, dataset_status_filename_1, dataset_status_filename_2):
        """
        Create a RepoModel object.

        :param pathtorepo: (string) the path to a local repository, which
        contains pairs of .ann and .txt files. No checking is done to guarantee
        that the repository is consistent.
        :return: None
        """

        dataset_source_file = None
        if dataset_source_filename != "": 
            dataset_source_file = open(dataset_source_filename, "w", encoding="utf-8", errors='ignore')

        dataset_status_file_1 = None
        if dataset_status_filename_1 != "": 
            dataset_status_file_1 = open(dataset_status_filename_1, "w", encoding="utf-8", errors='ignore')

        dataset_status_file_2 = None
        if dataset_status_filename_2 != "": 
            dataset_status_file_2 = open(dataset_status_filename_2, "w", encoding="utf-8", errors='ignore')

        date_errors_file = open("date_errors.txt", "w", encoding="utf-8", errors='ignore')

        if mode == "annotate":
            print("Loading classifiers for status and source...")

            status_rfc = pickle.load(open(status_rfc_filename, 'rb'))
            status_bc = pickle.load(open(status_bc_filename, 'rb'))
            status_bc_date = pickle.load(open(status_bc_date_filename, 'rb'))

            source_bc = pickle.load(open(source_bc_filename, 'rb'))
            
            print("Classifiers loaded.")
        else:
            status_rfc = None
            status_bc = None
            status_bc_date = None
            source_bc = None

        # Each document is saved as a textunit.
        self.documents = {}

        if os.path.isdir(ann_dir):
            for path in iglob("{0}/*.ann".format(ann_dir)):
                try:
                    # The key of each document is the document name without
                    # the suffix (i.e. "001.ann" becomes "001")
                    key = os.path.splitext(path)[0]

                    txt_file_path = key + '.txt'
                    age, sex = AgeSexImporter.extract_age_sex_from_file(txt_file_path)

                    key = os.path.split(key)[-1]

                    context = processann(mode, path, age, sex, status_rfc, status_bc, source_bc, dataset_source_file, dataset_status_file_1, dataset_status_file_2, date_errors_file, status_bc_date)

                except KeyError as e:

                    print("Parse error for document {}: {}, {} \n".format(str(path),
                                                            str(e),
                                                            sys.exc_info()[0])
                                                            )

        else:
            raise IOError(u"{0} is not a valid directory".format(ann_dir))

        if not dataset_source_file is None: dataset_source_file.close()
        if not dataset_status_file_1 is None: dataset_status_file_1.close()
        if not dataset_status_file_2 is None: dataset_status_file_2.close()

        date_errors_file.close()
