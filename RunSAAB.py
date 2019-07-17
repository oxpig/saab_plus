import os, json, sys, ast
import pandas as pd
import multiprocessing as mp
from argparse import ArgumentParser
from itertools import tee
from aboss_utils.ProgressBar import returnProgress
from code.StructuralAlignment import align_single_sequence
from code.DataManagement.SAbDab import structural_reference
from code.PrepareForSAAB import oas_output_parser
import logging
formatLoops = {"cdrh1":"H1","cdrh2":"H2","cdrh3":"H3Seq",
               "cdrl1":"L1","cdrl2":"L2","cdrl3":"L3Seq"}

def find_redundancy(redundancy):
    """if redundancy is not integer
        return 1
    """
    try:
        return int(redundancy)
    except:
        return 1

def prepare_saab_data(sequence):
    """
    Extracting data from anarci outputs and
    preparing data for SAAB+
    """
    cdr3sequence = sequence.CDRH3
    VGene = sequence.VGene[:5]
    Numbered = json.loads(sequence.Numbered)
    CDRs = [loop for loop in Numbered.keys() if "cdr" in loop]
    SeqInfo = { formatLoops[loop] : Numbered[loop] if "3" not in loop else cdr3sequence for loop in CDRs  }
    SeqInfo["V"] = VGene
    SeqInfo["Redundancy"] = find_redundancy(sequence.Redundancy)
    return ( sequence.Sequence, oas_output_parser(Numbered), SeqInfo)

class RunSaab(object):
    """
    Class that initiates saab plus
    Inputs are:
        input_file - anarci parsed and structurally filtered txt file
                     Generated by run_ANARCI_parsing.py module
    """
    def __init__(self, input_file, output_name, output_dir):
        self.input_file = input_file
        self.output_name = output_name
        self.output_dir = output_dir
        assert os.path.isfile(self.input_file), "Input file does not exist"
        self.strucs = structural_reference()
        logging.info("\tNumbered PDBs have been loaded into memory")
        self.rows_to_skip = 0
        self.currently_analysed = 0
        self.chain  = "Heavy"

    def create_output_dir(self):
        try:
            os.makedirs(self.output_dir)
            logging.info("Output Directory has been created: {0}".format(self.output_dir))
        except:
            logging.info("Output Directory already exists")

    def initiate_SAAB(self, ncpu):

        if os.path.isfile( os.path.join(self.output_dir, self.output_name) ):
            self.rows_to_skip = self.to_skip()
            logging.info("SAAB annotated file already exists.\n Checking the number of rows to skip: {0}".format( self.rows_to_skip))
    
        # Creating an iterator and counting total number of entries
        iterator = pd.read_csv(self.input_file, header=None, iterator=True, chunksize=60000, sep=",", 
                                names=["Sequence","Redundancy", "CDRH3", "Aboss1", "Aboss2", "VGene","JGene", "Numbered", "Track"],
                                skiprows=self.rows_to_skip)
        df_iterator, total_number_iterator = tee(iterator)
        total_dataunit_size = sum([ chunk.shape[0]  for chunk in total_number_iterator])
        for chunk in df_iterator :
            data_for_saab = []
            for sequence in chunk.itertuples():
                data_for_saab.append( prepare_saab_data(sequence))
                self.currently_analysed += 1
            logging.info( returnProgress(float(self.currently_analysed) / total_dataunit_size)) 
            pool = mp.Pool(processes=ncpu)
            results = [ pool.apply_async(align_single_sequence, args = (data_for_saab[i::ncpu], self.strucs,\
                                                                        self.chain )) for i in xrange(ncpu) ]
            pool.close()
            self.writing_output(results)
            del results

        self.gzip_file()
        self.create_output_dir()
        os.rename("{0}.gz".format(self.output_name), os.path.join(self.output_dir,"{0}.gz".format( self.output_name)))
        logging.info("{0} has been structurally annotated \n".format( os.path.join(self.output_dir, self.output_name))) 

    def gzip_file(self):
        os.system('gzip -f '+self.output_name)

    def writing_output(self, results):
        correct_sequences_portion = [ r.get() for r in results ]
        with open(self.output_name, "a") as txtFile:
            for portion in correct_sequences_portion:
                for seq in portion[0]:
                    txtFile.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(seq, 
                                                                             portion[0][seq][0], 
                                                                             portion[0][seq][1], 
                                                                             portion[0][seq][2], 
                                                                             portion[0][seq][3],
                                                                             portion[0][seq][4],
                                                                             portion[0][seq][5]))
            del portion
            del correct_sequences_portion

    def to_skip(self):
        df = pd.read_csv(os.path.join( self.output_dir, self.output_name) , header=None, sep="\t", 
                                         names=["seq", "H3pdb", "Canon", "Redundancy",
                                                "FrameWork", "CDRHSeq", "ESS"])
        return len(df)

def initArgParser():

    parser = ArgumentParser(description=__doc__)
    group = parser.add_argument_group('input_file arguments')
    group.add_argument('-f', action='store', dest='filename', default=False,
                        help="ANARCI parsed file")
    group.add_argument('-n', action='store', dest='ncores', default=16, type=int,
                        help="number of cores to use in multiprocessing")
    group.add_argument("-o", action="store", dest="output_name", default="output_structure.txt",
                        help="Output output_name")
    group.add_argument("-d", action="store", dest="output_dir", default=".",
                        help="Output directory name")
    return parser

def printStatus(args):
    print "   FILENAME: {0}".format(args.filename)
    print "      CORES: {0}".format(args.ncores)
    print "Output FILE: {0}".format(args.output)
    print " Output Dir: {0}".format(args.output_dir)
    return vars(args)

if __name__ == "__main__":

    parser = initArgParser()
    args = parser.parse_args()

    input_file = args.filename
    ncpu = args.ncores
    output = args.output
    output_dir = args.output_dir
    arguments = printStatus(args)
    
    if not args.filename:
        raise AssertionError("Filename is not specified")

    saab_instance = RunSaab(input_file, output, output_dir)
    saab_instance.initiate_SAAB(ncpu)
