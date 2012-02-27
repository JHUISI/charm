#!/bin/sh
gnuplot <<EOF

set terminal postscript eps enhanced "Helvetica" 24;
set size 3,1.33333;
set output "DoS_Attack.eps";
set yrange [1 : 825]; set y2range [0:0.55]; set xrange[0 : 75100];
set y2tics border;
set title "Automatically Generated BLS Batch Verifier: Performance During DoS Attack" font "Helvetica,28";
set xlabel "Cumulative Time (ms)" font "Helvetica,28";
set ylabel "Signatures / sec" font "Helvetica,28";
set y2label "Invalid Signatures as Fraction of Total" font "Helvetica,28";

set style line 1 lt 1 lw 8 pt 3
set style line 2 lt 4 lw 8 pt 3
set style line 3 lt 2 lw 8 pt 3
set style line 4 lt 3 lw 8 pt 3

f(x) = m*x + b

fit f(x) "PER_INVALID_SIGS" using 1:2 via m,b

plot "SPS_ABOVE" w lines ls 1 title "Batch + Individual Verifier", \\
	"SPS_BELOW" w lines ls 3 title "Batch-Only Verifier", \\
	f(x) w lines ls 2 title "Invalid Signatures as Fraction of Total" axes x1y2;

EOF
