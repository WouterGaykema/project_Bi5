# general info for `main_script.py`

# important files to set
<sub>  (Within `main_script.py` ) </sub>
#### `FASTA_DATABASE : str `
string holding (complete) path to the filename of the main database to query with hmmsearch

#### `MAIN_FASTA_FILENAME : str`
string holding (complete) path to the main dataset of fasta files to create MSA’s with

#### `FASTA_TOADD_FILENAME : str `
string holding (complete) path to the file that keeps track of fasta sequences from this iteration. Will be added to MAIN_FASTA_FILENAME when the next iteration starts and then the file is cleared to start over. Only fasta files not previously existing in MAIN_FASTA will be added here.

# global variables
#### `DEFAULT_SELECTION : list[str]`
list of columns (as strings) used in fetching data from uniprot  
```
default = [ "go(biological process)",
            "go(cellular component)",
            "go(molecular function)"]
```


#### `HMMSEARCH_OPTIONS : str`
options to pass to the commandline call `>hmmsearch <options> hmm_file database`  

taken from the HMMER manual:  
`--tblout <f>` Save a simple tabular (space-delimited) file summarizing the
per-target output, with one data line per homologous target
sequence found.   
`--acc` Use accessions instead of names in the main output, where
available for profiles and/or sequences.  
`--noali` Omit the alignment section from the main output. This can greatly reduce the output volume.


```
default = " --tblout " + HMM_SEARCH_TAB_OUTPUT_FILENAME + " --acc --noali "
```
###### <sub>note:`HMM_SEARCH_TAB_OUTPUT_FILENAME` is a global string that holds filename hmmsearch output should be directed to.  </sub>

# temp filenames
set as you like, not that it matters. As they're not overlapping. duh.
```MSA_FILENAME = 'msa.msa'
HMM_FILENAME = 'hmm.hmm'
HMM_SEARCH_TAB_OUTPUT_FILENAME = 'hmmsearch3_tab_output.tbl'
BLAST_OUTPUT = 'blast_output.xml'
LOG_FILENAME = 'logfile.log'
```

# main program
### init
- initialise database object with connection to our FASTA_DATABASE
- initialise `bioservices.Uniprot.Uniprot` object to handle Uniprot requests
- fetch highest iteration from the database

### outer '`running`' loop
purpose: create MSA's from main dataset (fastas), create HMM from MSA, do a `phmmsearch` against a locally downloaded version of the uniprot database.
- create MSA
- create HMM
- do HMMsearch
- set loopcount = 0
  - used to print the amount of loops made ocasionally.
- set innerLoop var to True
  - deprecated
  - `DEPRECATEME`
- create generator that spits out identifiers from the tabular output that HMMsearch generates




### inner iteration over hmmsearch results
This loop works by calling next() on the generator to retrieve an identifier (and an e-value that we don't use atm)
- get identifier
- check if identifier exists in our database  
-