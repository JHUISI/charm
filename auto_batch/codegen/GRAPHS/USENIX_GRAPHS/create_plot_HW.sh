#!/bin/sh
rm -f *.eps
gnuplot <<EOF

set terminal postscript eps enhanced color 'Helvetica' 10;
set size 0.425,0.425;
set output 'hw_single_multiple_MNT_160_codegen.eps';
set yrange [0 : 25]; set xrange[1 : 100]; set xtics autofreq 20;
set title 'MNT160' font 'Helvetica,10';
set xlabel 'Number of signatures';
set ylabel 'ms per signature';
plot 'HW_bat.dat' w lines lw 6 title 'HW-Single (batched)', \\
 'HWDIFF_bat.dat' w lines lw 6 title 'HW-Multiple (batched)', \\
 'HW_ind.dat' w lines lw 6 title 'HW (individual)';
