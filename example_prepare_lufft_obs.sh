#!/bin/bash

cd /mnt/c/Users/graha/Documents/AASO/OBSGRID/python_scipts

export LFILE=//mnt/c/Users/graha/Documents/AASO/python_scripts/eclipse_plot/Tolten_10s_avg_timefix.txt
export STIME=2020,12,14,15,00,00
export ETIME=2020,12,14,18,00,00
export SDIR=//mnt/c/Users/graha/Documents/AASO/OBSGRID/OBSGRID/
export LAT=-39.236
export LON=-73.161
export ELEV=3

python lufft2littler.py $STIME $ETIME $LFILE $SDIR $LAT $LON $ELEV

export STIME=20201214150000
export ETIME=20201214180000
export INDIR=$SDIR
export TINTV=10800

python littler2date.py $STIME $ETIME $INDIR $SDIR $TINTV

echo DONE
