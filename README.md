[![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/download/releases/2.7/)


# Structural Annotation of BCR Repertoires
SAAB+: annotation of BCR Repertoires with structural information, using separate tools
to map CDR loop sequences to repersentative antibody structures.  
SAAB+ support analysis of both heavy and light chain BCR repertoire data.

## Getting Started
Please follow instructions below to install SAAB+ pipeline on our machine

### Prerequisites
SAAB+ comes with the antibody customized version of **FREAD** package.  
**anarci** and **scalop** are not supplied, and need to be downloaded separately.

> * [anarci v1.3](http://opig.stats.ox.ac.uk/webapps/newsabdab/sabpred/anarci) - is the antibody sequence numbering tool. In SAAB+ pipeline, ANARCI is used to filter the sequences for structural viability. Upon installation, ANARCI automatically downloads the latest version of IMGT germlines.
> * [scalop](http://opig.stats.ox.ac.uk/webapps/newsabdab/sabpred/scalop) - is the antibody canonical class annotation tool. SCALOP is downloaded with the latest version of antibody canonical classes.
> * [hmmer](http://hmmer.org/download.html) - is required to build antibody HMM profiles, which are used in the ANARCI numbering step. ANARCI was tested with 3.1b2 hmmer version.

### Installing

To install SAAB+ as root run:

```
python setup.py install
```
For users without root access install locally using:

```
python setup.py install --user
```
## Checking installation
To check if installation was successful, simply run
```
SAAB_PLUS_DIAG
```
This script generates __diagnostics.log__.  
If installation was successful, the diagnostics.log should look like:
```
2019-12-16 12:33:46,796 INFO 	Writing DIAGNOSTICS log

2019-12-16 12:33:46,950 INFO  Successfully imported: anarci
2019-12-16 12:33:46,950 INFO  Successfully imported: anarci germlines
2019-12-16 12:33:46,952 INFO  Successfully imported: anarci Accept
2019-12-16 12:33:46,955 INFO  Successfully imported: scalop
2019-12-16 12:33:48,431 INFO  Successfully imported: scalop assing
2019-12-16 12:33:48,475 INFO  Successfully imported: FREAD
2019-12-16 12:33:48,476 INFO  Successfully imported: FREAD ESS table
2019-12-16 12:33:48,476 INFO  Successfully imported: prosci module
2019-12-16 12:33:48,478 INFO  Successfully imported: Common module
2019-12-16 12:33:48,479 INFO   PDB template info file for H3 loop is located: OK
2019-12-16 12:33:48,479 INFO   PDB template info file for L3 loop is located: OK
2019-12-16 12:33:48,479 INFO   CDR-H3 cluster mapping file is located: OK
2019-12-16 12:33:48,480 INFO   CDR-L3 cluster mapping file is located: OK
2019-12-16 12:33:48,513 INFO   Directory with PDB frameworks for H3 loop is located: OK
2019-12-16 12:33:48,546 INFO   Directory with PDB frameworks for L3 loop is located: OK
2019-12-16 12:33:48,547 INFO  Directory with FREAD templates for H3 loop is located: OK
2019-12-16 12:33:48,854 INFO  Number of FREAD templates found: 3759
2019-12-16 12:33:48,854 INFO  Directory with FREAD templates for L3 loop is located: OK
2019-12-16 12:33:49,152 INFO  Number of FREAD templates found: 3606
2019-12-16 12:33:49,808 INFO  Imported pandas, Version 0.24.2
2019-12-16 12:33:49,812 INFO  Imported Bio, Version 1.70
```
If any __ERROR__ were recorded in diagnostics.log, you will not be able to initialise SAAB_PLUS
### Running a test example
SAAB+ takes antibody sequences in the fasta format as the input. e.g.
>&gt;seq1  
>SLRLSCAASGFTFSGHWMYWVRQAPGKGLVWVARINND.....  
>&gt;seq2  
>SLRLSCAASGFTFRSYWMSWVRQAPGRGLEWIARINND.....

The EXAMPLE folder contains a test fasta file.
To run SAAB+ pipeline on human BCR data across twenty CPU cores  
```
SAAB_PLUS -f Fasta_example.fa -n 20 -s human
```
### Interpreting SAAB+ outputs
SAAB+ outputs a zipped tab-delimited text file.
```
            Protein_Seq - Full antibody amino acid sequences. Only sequences that passed anarci structural viability assessment are retained.  
   CDR-{H3,L3}_template - CDR-{H3,L3} structure that was predicted by FREAD  
{H1,L1}_Canonical_Class - SCALOP predicted CDR-{H1,L1} canonical class
{H2,L2}_Canonical_Class - SCALOP predicted CDR-{H2,L2} canonical class
             Redundancy - Number of Proiten_Seq copies in the input fasta file  
     Framework_template - PDB structure that was used in CDR-{H3,L3} structure prediction  
   CDR-{H3,L3}_sequence - Sequence of CDR-{H3,L3} loop  
                    ESS - FREAD score for the predicted CDR-{H3,L3} structure  
             Annotation - Sequnces, whose FREAD CDR-{H3,L3} structure prediction scores were above the quality threshold      
               Clusters - CDR-{H3,L3} clusters (0.6A threshold)
```
