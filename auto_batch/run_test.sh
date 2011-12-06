#!/bin/bash

rm -f *.log
main=batchverify.py

for sch in bls chp chch cyh hess boyen waters bgls
do
   echo -n "Running signature scheme: $sch..."
   python $main "$sch".bv > "$sch".log
   echo "ok" 
done

mv *.dat plots/

exit 0
