#!/bin/sh
rm -f *.pdf *.eps
gnuplot <<EOF

set terminal postscript eps enhanced color "Helvetica" 14;
set size 5.5,2;
set output "CHP_performance.eps";
set yrange [0 : 40]; set xrange[1 : 100];
#set y2tics border;
set title "CHP Verification Performance" font "Helvetica,25";
set xlabel "Number of signatures" font "Helvetica,20";
set ylabel "Signatures / sec" font "Helvetica,20";
#set y2label "% invalid signatures" font "Helvetica,20";


set style line 1 lt 1 lw 7 pt 3 lc rgb "black"
set style line 2 lt 4 lw 7 pt 3 lc rgb "gray"
#set style line 3 lt 2 lw 7 pt 3 lc rgb "dark gray"


plot "batchOutput" w lines ls 1 title "Batch Verification", "indOutput" w lines ls 2 title "Individual Verification";

EOF
