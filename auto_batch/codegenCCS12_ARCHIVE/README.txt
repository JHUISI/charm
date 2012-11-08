This file contains instructions for the following:

-- How to run CodeGen for the schemes listed in the CCS paper.

The following contains instructions for each of the schemes in the CCS paper.

1)  BLS
The files are contained in charm/charm/auto_batch/codegen/BLS

Here are the files you need:
A)  pksig_bls04.py => Charm implementation of BLS
B)  batchOutput_BLS => batcher's output of BLS, manually modified so that all dictionary entries show the
dictionary name and numerical index.  For example, if you were referring to something as g, but it actually
came from a dictionary such as the one below:

pk = {'g': g}

You would change all instances of "g" in batchOutput_BLS to "pk#0?" (no quotation marks).  The numerical
index be encased by a "#" on the left and a "?" on the right (no quotation marks).  The reason for the 
"?" on the right (no quotation marks) is that I need to be able to know whether pk#x - 1 is actually 
pk#x - 1, or pk#(x - 1)

Now run this command:

python ../AutoBatch_CodeGen.py pksig_bls04.py batchOutput_BLS dummyParamNotUsed [output name for individual
signature verification file] [output name for batch signature verification file] [output name for 
divide-and-conquer file for batch signature verification]

Please note that the last three arguments (the output names) must end in the ".py" suffix so that they
are legitimate Python files.

This should produce the three Charm files for individual signature verification, batch signature
verification, and the divide-and-conquer routine for batch signature verification.

The remaining cases are run mostly the same, with the exception of the 2 input files (the Charm description
of the scheme and batcher's output).  As a result, I'll only list those 2 files in describing how to run
the remaining schemes.

2)  CHP
Folder:  charm/charm/auto_batch/codegen/CHP
Charm description file:  pksig_chp.py
Batcher output file, modified so all dictionary entries are encased with # and ? -> batchOutputCHP

3)  
