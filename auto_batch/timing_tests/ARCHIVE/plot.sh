#!/bin/sh
rm -f *.pdf *.eps
gnuplot <<EOF

set terminal postscript eps enhanced "Helvetica" 24;
set size 3,2;
set output "VARIED_INVALID_SIGS_DETERMINISTIC_NOcountermeasures.eps";
set yrange [1 : 850]; set y2range [0:0.2]; set xrange[0 : 76000];
set y2tics border;
set title "Without Countermeasures" font "Helvetica,28";
set xlabel "Cumulative Time (ms)" font "Helvetica,28";
set ylabel "Signatures / sec" font "Helvetica,28";
set y2label "Fraction of Invalid Signatures" font "Helvetica,28";


set style line 1 lt 1 lw 8 pt 3
set style line 2 lt 4 lw 8 pt 3
set style line 3 lt 2 lw 8 pt 3
set style line 4 lt 3 lw 8 pt 3

plot "sigsPerSec_VARIED_DETERMINISTIC" w lines ls 1 title "Signatures / sec (without countermeasures)", \\
	"percentInvalid_VARIED_DETERMINISTIC" w lines ls 2 title "Fraction of Invalid Signatures (without countermeasures)" axes x1y2, \\
	"IndLine" w lines ls 3 title "Individual Verification";

#plot "sigsPerSec_VARIED_O1_DETERMINISTIC" w lines ls 1 title "Signatures / sec (with countermeasures)", \\
#	"percentInvalid_VARIED_O1_DETERMINISTIC" w lines ls 2 title "Fraction of Invalid Signatures (with countermeasures)" axes x1y2, \\
#	"IndLine" w lines ls 3 title "Individual Verification";

EOF
