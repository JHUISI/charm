#!/bin/sh
gnuplot <<EOF

set terminal postscript eps enhanced "Helvetica" 24;
set size 3,2;
set output "testPlot.eps";
set yrange [0 : 100]; set xrange[0 : 100];
set y2tics border;
set title "AutoBatch Performance During DoS Attack" font "Helvetica,28";
set xlabel "Cumulative Time (ms)" font "Helvetica,28";
set ylabel "Signatures / sec" font "Helvetica,28";

set style line 1 lt 1 lw 8 pt 3
set style line 2 lt 4 lw 8 pt 3
set style line 3 lt 2 lw 8 pt 3
set style line 4 lt 3 lw 8 pt 3

f(x)=m*x+b
fit f(x) "linearNos.dat" using 1:2 via m,b


plot f(x) title "Line Fit"

EOF
