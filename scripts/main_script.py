from sys import argv
import subprocess
import os.path
import re

from time import sleep

from Bio import SearchIO
from bioservices import UniProt
from DbConnector import DbConnector

#important globals

# regex object used in find_target_pattern(string):
TARGET_PATTERN = re.compile('[C]..[C]')

# entry-point filenames
FASTA_DATABASE = '/home/queue/SwissProt/uniprot_sprot.fasta.gz'#must be zip.gz!
FASTA_FILENAME = 'in_data/uniprot_seqs_rev.fasta.fasta'

# temp filename
MSA_FILENAME = 'msa.msa'
HMM_FILENAME = 'hmm.hmm'
HMM_SEARCH_TAB_OUTPUT_FILENAME = 'hmmsearch3_tab_output.tbl'
BLAST_OUTPUT = 'blast_output.xml'
LOG_FILENAME = 'logfile.log'


# columns used in fetching data from uniprot
DEFAULT_SELECTION = ["go(biological process)","go(cellular component)",
                     "go(molecular function)"]

# searchoptions for hmmsearch
HMMSEARCH_OPTIONS = " --tblout " + HMM_SEARCH_TAB_OUTPUT_FILENAME + \
                    " --acc --noali "

# custom errors
class TooManyError(Exception):
    """When there's too much of something"""
    def __init__(self, message="Too many. That was unexpected!"):
        super().__init__(message)

class InvalidIdError(Exception):
    """When using an identifier yield unexpected results"""
    def __init__(self, message="That ID can't be found or doesn't exist"):
        super().__init__(message)

class UrgentUnknownError(Exception):
    """When I dont know what in fruits name happened"""
    def __init__(self, message):
        message = "CALL HELP IMMEDIATELY " + message
        super().__init__(message)



# helper functions
def find_target_pattern(string):
    """ Uses a regex object to find all occurences of
        a pattern within a string.

        The purpose (at this moment) is to only
        return values when only one unique match is found.

        An error will be raised when more than 1 match is found
    """
    # set TARGET_PATTERN as global re.compile('regexstring')
    matches = TARGET_PATTERN.findall(string)
   
    if matches:
        match_amt = len(matches)
        if match_amt > 1:
            raise TooManyError
        elif match_amt == 1:
            match = matches[0]
            return match
    else:
        return None
        
def create_msa_mafft(fasta_filename=FASTA_FILENAME,
                     msa_destination_filename=MSA_FILENAME, verbose=False):
    """calls 'mafft' through the shell to create a
       multiple sequence alignment (msa_filename)

    ARGS:
        fasta_filename: string
            relative path (just a filename) of a file containing fasta
            sequences to be aligned

        msa_destination_filename: string
            relative path in which to save the multiple sequence alignment

    """

    # Check whether msa has already been made
    if os.path.isfile(msa_destination_filename):
        print("msa already exists, overwriting!")
    # Execute command if msa hasn't been made before

    cmd = "mafft " + fasta_filename + " > " + msa_destination_filename
    e = subprocess.check_call(cmd, shell=True)
    if verbose:  print(e)
    return

def create_hmm(msa_filename=MSA_FILENAME,
               hmm_destination_filename=HMM_FILENAME, verbose=False):
    """calls 'hmmbuild' through the shell to create a hmm profile
       from a multiple sequence alignment (msa_filename)

    ARGS:
        msa_filename: string
            relative path (just a filename) of
            a file containing a valid MSA

        hmm_destination_filename: string
            relative path in which to create
            a hmm profile using hmmer

    """

    # Check whether hmm has already been made
    if os.path.isfile(hmm_destination_filename):
        print("hmm already exists, overwriting!")
    # Execute command if hmm hasn't been made before

    cmd = "hmmbuild " + hmm_destination_filename + " " + msa_filename
    e = subprocess.check_call(cmd, shell=True)
    if verbose:  print(e)
    return

def do_hmm_search(hmm_filename=HMM_FILENAME,
                  fasta_database=FASTA_DATABASE,
                  options= HMMSEARCH_OPTIONS ,
                  verbose=False):
    """calls 'hmmsearch' through the shell to ty and
       create a  TODO <whatever the format is>
       by performing a hmmsearch on a database file

    ARGS:
        hmm_filename: string
            relative path (just a filename) of
            a file containing a valid profile HMM

        fasta_database: string
            relative path to a (fasta) database file
            examples @ https://www.uniprot.org/downloads

    """

    # Check whether hmm has already been made
    if os.path.isfile(hmm_filename):
        pass
    # Execute command if hmm hasn't been made before
    else:
        cmd = "hmmsearch {} {} {}".format(options,hmm_filename,fasta_database)
        e = subprocess.check_call(cmd, shell=True)
        if verbose:  print(e)
    return


def fetch_fasta_from_local_zip_db(accession, local_zip_db_name=FASTA_DATABASE):
    """ hacky function to gather header + sequence by acession in a
        downloaded database file (zipped fasta)
        """
    with gzip.open(gzip_db_location, 'rt') as db_as_zipfile:
        header = ''
        seq = ''
        for line in db_as_zipfile:
            if line.startswith(">") and header != '':
                print(header, "\n",seq)
                if seq != '':
                    return header, seq
                else:
                    # TODO MAKE CUSTOM EXCEPTION
                    raise Exception("seq not filled in"+\
                        "fetch_fasta_from_local_zip_db!")
            
            if accession in line:
                header = line.strip("\n")

            if header != '' and not line.startswith(">"):
                seq += line.strip("\n")

        # TODO MAKE CUSTOM EXCEPTION
        raise Exception("something weird happened in"+\
                        "fetch_fasta_from_local_zip_db")
                

# prolly not gonna use lol
def fetch_fasta_from_uniprot(uniprot_handle, acession, verbose=False):
    """should return the header+sequence of a swissprot entry in
       fasta format, but otherwise lets you know it didn't.

    arguments
    uniprot_handle: bioservices.Uniprot object to execute the fetch

    acession: str (preferrably), can be a list too. Let's keep it
              the way bioservices had it made. very convenient.

    returns: str containing a fasta file for max 1 entry

    throws: all kinds of errors. Wrong id error, too many
            (unexpected result) errors,
            400, 404 errors.
            UnknownError s.

    
    """
    fasta_str = uniprot_handle.retrieve(acession, frmt='fasta')
    if verbose: print('got a fasta from', acession)
    print(fasta_str)
    if type(fasta_str) == str:
        # sometimes this dumb retrieve func returns just 1 string,
        # the fasta itself. This is the expected result
        return fasta_str
    
    elif type(fasta_str) == list:
        # but then, sometimes, like if you accidentally were to give it 2
        # acession identifiers, it would return a list of fasta strings.
        raise TooManyError('fetch_fasta returned too many fasta strings!')
    
    elif (fasta_str == '404') or (fasta_str == 404):
        # then if an id returns a 404 page, it just returns '404'
        # so that's really convenient, too, yes.
        raise InvalidIdError(str(acession) + " yields a 404 error!")

    elif (fasta_str == '400') or (fasta_str == 400):
        # oh apparently something can cause it to return a 400 error too
        raise InvalidIdError(str(acession) + " yields a 400 error!")
    else:
        # gosh darnit
        raise UrgentUnknownError('type fasta_str:' + str(type(fasta_str)) +
                                 ' acession id:' + str(acession))



def get_uniprot_stuff(uniprot_handle, acession, columns_list=DEFAULT_SELECTION,
                      verbose=False):
    """ TODO DOCSTRING
        in goes a Uniprot object from bioservices along with a
        swissprot id and a list of expected columns

        """
    
    result = uniprot_handle.search(acession, columns=",".join(columns_list))

    column_value_dict = dict()

    for i, column in enumerate(columns_list):
        if verbose:
            print(i)
            print(column, result.split("\n")[1].split("\t")[i-1])   #TODO FIX THIS UGLY THING
            try:
                value = result.split("\n")[1].split("\t")[i]
            except IndexError:
                value = None              

            column_value_dict[column] = value
        
    return column_value_dict


def iterate_hmm_search_tab_results(filename=HMM_SEARCH_TAB_OUTPUT_FILENAME
                                   , verbose=False):
    """ GENERATOR!!!
        iterate over hmmsearch3 tab output using SearchIO.parse

    yields:
        Bio.< ? ? >.Hit.id
        Bio.< ? ? >.Hit.evalue

    """
    result = next(SearchIO.parse(filename, 'hmmer3-tab'))
    for hit in result.hits:
        yield hit.id, hit.evalue
    
    
def make_obscure_SQL_part(d):
    """ takes a dictionary and puts the value in the right order
        based on the order of keys in the database
        with quotes so it can be entered as a string/text in a sql insert"""
    keys_in_order = [k for k in DEFAULT_SELECTION]
    return "'" + "','".join([d[k] for k in keys_in_order]) + "'"
        

def important_mainloop(verbose=True):
    # todo set verbose default to False again one day or another im gonna find ya im gonna getcha getcha getcha getcha

    # create an object to handle communications with mySQL database
    db = DbConnector() 
    

    # create uniprot handle object
    # todo: find out if 'handle' is the right terminology here
    uniprot_handle = UniProt(verbose=True)


    # determine input file(s)
        # check validity
        # combine multiple fasta's into one for msa

    
    # set main loop condition
    # this could be NOT running out of results or
    # having more than 50% of results be results we already
    # found
    running = True
    iteration = 0 # TODO function to get highest iteration from db
                  # and then we should actually check if
                  # the current file we're working on
                  # has been finished before increasing it
    
    # 'running' loop
    while running:
        
        # msa
        
        create_msa_mafft()
        if verbose: print("main: trying to create msa...")

        # hmm
        create_hmm()
        if verbose: print("main: trying to create phmm...")

        # hmm search
        do_hmm_search()
        if verbose: print("main: trying to do hmmsearch...")
#TODO

        # iterate hmm search results
        innerLoop = True
        loopcount = 0
        while innerLoop:

            if verbose:
                if loopcount % 10 ==0:
                    print('fasta files:', loopcount)
                    
            identifier, evalue = iterate_hmm_search_tab_results()

            actual_id = identifier.split("|")[1]

            # sql select to check if it exists in our db
            if db.exists_protein(actual_id):
                continue  # skip (doesnt check if other values filled though)
            else:
    
                # deprecated as we have a local database now
                # fetch_fasta_from_uniprot(uniprot_handle, acession)


                # fetch header, fasta from local database
                header, seq = fetch_fasta_from_local_zip_db(actual_id)

                pos_2c = find_target_pattern(seq)
                GO_STUFF_D = get_uniprot_stuff(uniprot_handle, acession)
                obscure_GO_stuff = make_obscure_SQL_part(GO_STUFF_D)
                
                query = f"""INSERT INTO PROTEIN VALUES(
                        NULL,
                        '{actual_id}',
                        '{header}',
                        '{seq}',
                        {iteration},
                        {GO_STUF_D['go(biological process)']},
                        {GO_STUF_D['go(cellular component)']},
                        {GO_STUF_D['go(molecular function)']},
                        {pos_2c});
                        """
                
                db.commit_query(query)

        #outofinnerloop
        iteration += 1

                    
        
        
        # repeat?
    
def main():

    # exceptions 
    caughtMistakes = {"noerror":0}


    while caughtMistakes[max(caughtMistakes)] < 5:
        """ as long as there are no errorcounts over 5,
            retry this loop"""
        try:
            important_mainloop()

        # exceptions we know how to handle
        #
        # here.

        # uknown exceptions
        except Exception as SomeUknownException:
            e = str(type(SomeUknownException))
            
            if str(e) in caughtMistakes:
                caughtMistakes[e] += 1
                
            else:
                caughtMistakes[e] = 1

            if caughtMistakes[e] > 5:

                print('too many exceptions caught of identical type')
                
                
            sleep(1000)
            
        print(caughtMistakes)

        with open('logfile.log', 'a') as logfile:
            for k, v in caughtMistakes.items():
                logfile.write(k + "\t\t" + str(v) + "\n")

    
        
            
        

    


if __name__ == "__main__":
    print('running from main')
    main()

