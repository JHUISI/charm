#!/bin/bash

rm *.dat *.log
main=batchverify.py

for sch in bls2 chp2 chch cyh hess boyen waters bgls
do
   echo -n "Running signature scheme: $sch..."
   python $main "$sch".bv > "$sch".log
   echo "ok" 
done

mv *.dat plots/

exit 0
