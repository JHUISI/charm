#!/bin/sh
gnuplot <<EOF

set terminal postscript eps enhanced color 'Helvetica' 10;
set size 0.425,0.425;
set output 'CDH_HW_DIFF_MNT_160_codegen.eps';
set yrange [0 : 25]; set xrange[1 : 100]; set xtics autofreq 20;
set title 'MNT160' font 'Helvetica,10';
set xlabel 'Number of signatures';
set ylabel 'ms per signature';
plot 'CDH_bat.dat' w lines lw 6 title 'HW-Single (batched)', \\
 'HW_DIFF_bat.dat' w lines lw 6 title 'HW-Multiple (batched)', \\
 'CDH_ind.dat' w lines lw 6 title 'HW (individual)';
