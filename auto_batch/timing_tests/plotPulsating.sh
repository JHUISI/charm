#!/bin/sh
rm -f *.pdf *.eps
gnuplot <<EOF

set terminal postscript eps enhanced color "Helvetica" 14;
set size 5.5,2;
set output "SigsPerSec_InvalidPercent.eps";
set yrange [0 : 1]; set xrange[0 : 0.2];
set y2tics border;
set title "Stats for BLS in batch mode" font "Helvetica,10";
set xlabel "Cumulative time (ms)";
set ylabel "SIGS/SEC";
set y2label "% INVALID SIGS";
plot "invalidPulsatingDistro" w lines lw 6 title "SIGS PER SECOND",;

EOF
