#######################################
#
# Graham Moss
# 07/01/2021
# graham.moss@umconnect.umt.edu
# :)
# 
#######################################
#
# Lufft surface data to littler format.
'''
This code takes in Lufft surface data (CSV), takes one minute averages,
then writes the code to littler format that can then be sorted using 
littler2date.py. 
'''
#time
#tot precip
#wind speed
#wind direction
#av air temp C
#fuel temp
#relative humidity,
#battery voltage
#av fuel moisture
#dir max gust,
#mx gust speed
#
# Imports
import datetime as dt
import numpy as np
import csv, os, sys
from re import search

if len(sys.argv) < 2:
    print('### ERROR ###\n' \
          'Must have 6 arguments provided\n' \
          'start time = YYYY,MM,DD,hh,mm,ss\n' \
          'end time = YYYY,MM,DD,hh,mm,ss\n' \
          'lufft_file = path_to_lufft_file.csv\n' \
          'save_directory = path_to_save_directory\n' \
          'latitude  = float\n' \
          'longitude = float\n' \
          'Elevation = float\n' \
          '### ERROR Exiting ###')
    sys.exit()

# User Inputs
#start_time  = sys.argv[1]
#end_time    = sys.argv[2]
#lufft_file  = sys.argv[3]
raw_dir = sys.argv[1]
save_dir    = sys.argv[2]
#latitude    = float(sys.argv[5])
#longitude   = float(sys.argv[6])
#Elevation   = float(sys.argv[7])
ID          = ''
Name        = 'RAWS'
Platform    = 'FM-12' #fixed surface observation
Source      = 'Land Station'

# definitions
def get_dp(T,RH):
    # This function calculates virtual temperature 
    # Source: https://www.weather.gov/epz/wxcalc_dewpoint
    a = 6.1121 #mbar
    b = 17.67
    c = 257.14 #deg C
    d = 234.5  #deg C
    def gammam(T,RH):
        return np.log(RH/100 * np.exp((b-T/d)*(T/(c+T))))
    return (c*gammam(T,RH))/(b-gammam(T,RH))+273.15

def get_time(tstring):
    # This function takes input times takes the aspects apart
    # 'YYMMDDhhmm'
    year    = int('20'+tstring[0:2])
    month   = int(tstring[2:4])
    day     = int(tstring[4:6])
    hour    = int(tstring[6:8])
    minute  = int(tstring[8:10])
    second  = 0
    return [year,month,day,hour,minute,second]

def headertime(time):
    # format time
    t = str(time)
    return t[:4]+t[5:7]+t[8:10]+t[11:13]+t[14:16]+'00'
    
def filedt(file):
    # format for name output
    return file[11:13]+file[14:16] + '_' + file[5:7]+file[8:10]+file[2:4]
    
def get_header(i,nvalid):
    return '%20.5f%20.5f%-40s%-40s%-40s%-40s%20.5f%10i%10i%10i%10i%10i' \
            % (latitude,longitude,ID,Name,Platform,Source,Elevation,nvalid, \
                missing,missing,missing,missing) + \
            3*(9*' '+'F') + '%10i%10i%20s' % (missing,missing,headertime(surf_time[i]))+ \
            13*('%13.5f' % missing + 6*' ' + '0') +'\n'

def get_data(nvalid):
    return 10*'%13.5f      0' % (avg_pres/nvalid,   \
                                 Elevation,         \
                                 avg_temp/nvalid,   \
                                 avg_dp/nvalid,     \
                                 avg_ws/nvalid,     \
                                 avg_wd/nvalid,     \
                                 avg_ws/nvalid * np.cos(np.deg2rad(avg_wd/nvalid)), \
                                 avg_ws/nvalid * np.sin(np.deg2rad(avg_wd/nvalid)), \
                                 avg_rh/nvalid,     \
                                 missing)+          \
                                 '\n'

def get_ending():
    return '-777777.00000      0-777777.00000      0-888888.00000      0-888888.00000      ' \
            '0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      ' \
            '0-888888.00000      0-888888.00000      0\n'

def get_tail(nvalid):
    return 3*'%7i' % (nvalid,0,0) +'\n'

def get_latlongelev(name,metafile):
    with open(metafile,'r') as mf:
        lines = mf.readlines()
    n = search('raws_(.*)_',name).group(1)
    
    for i,line in enumerate(lines):
        if line == n+'\n':
            loc = i
    
    return float(lines[loc+1][:-1]),\
           float(lines[loc+2][:-1]),\
           float(lines[loc+3][:-1])
    
    
# Build in one minute intervals
missing     = -888888.00000
#time
# convert start and end times to datetimes
#t1 = dt.datetime(*get_time(start_time))
#t2 = dt.datetime(*get_time(end_time))
# The beginning 4*_ in the save name signals the littler2date program
#   to open the file at every timestep.

# Read in lufft data
for entry in os.scandir(raw_dir):
    if os.path.basename(entry)[:4] == 'raws':
        savefile = '____' + os.path.basename(entry)[:-4] + '.littler'
        
        metafile = '//mnt/c/Users/graha/Documents/MSGC/raws/stationmetadata.txt'
        latitude,longitude,Elevation = get_latlongelev(os.path.basename(entry),metafile)
        
        #containers
        surf_time   = []
        surf_temp   = []
        surf_rh     = []
        surf_pres   = []
        surf_ws     = []
        surf_wd     = []
        with open(entry, newline='') as csvfile:
            surfs_dat = csv.reader(csvfile, delimiter=',')
            for surf in surfs_dat:
                time = dt.datetime(*get_time(surf[0]))
                surf_time.append(time)
                surf_temp.append(float(surf[4])) #C
                surf_rh.append(  float(surf[6])) #%
                surf_pres.append(missing)
                surf_ws.append(  float(surf[2])) #ms
                surf_wd.append(  float(surf[3]))#deg

        # Calculate Dew Point
        surf_dp     = []
        for i in range(len(surf_temp)):
            surf_dp.append(get_dp(surf_temp[i],surf_rh[i]))
            surf_temp[i] += 273.15 # degC to K
        avg_temp = 0
        avg_rh   = 0
        avg_pres = 0
        avg_ws   = 0
        avg_wd   = 0
        avg_dp   = 0
        # Loop Through all times and write data to outfile
        with open(save_dir+savefile,'w') as f:
            for i in range(len(surf_time)):
                if i == 0:
                    ltime = surf_time[i].hour
                    nvalid = 0; j = i
                    while surf_time[j].hour <= ltime:
                        nvalid += 1; j += 1
                    f.write(get_header(i,1))
                    avg_temp   += surf_temp[i]
                    avg_rh     += surf_rh[i]
                    avg_pres   += surf_pres[i]
                    avg_ws     += surf_ws[i]
                    avg_wd     += surf_wd[i]
                    avg_dp     += surf_dp[i]
                    
                elif surf_time[i].hour != ltime:
                    f.write(get_data(nvalid))
                    f.write(get_ending())
                    f.write(get_tail(1))
                    avg_temp   = 0
                    avg_rh     = 0
                    avg_pres   = 0
                    avg_ws     = 0
                    avg_wd     = 0
                    avg_dp     = 0
                    ltime = surf_time[i].hour
                    nvalid = 0; j = i
                    while surf_time[j].hour == ltime and surf_time[j] != surf_time[-1]:
                        nvalid += 1; j += 1
                    f.write(get_header(i,1))
                    avg_temp   += surf_temp[i]
                    avg_rh     += surf_rh[i]
                    avg_pres   += surf_pres[i]
                    avg_ws     += surf_ws[i]
                    avg_wd     += surf_wd[i]
                    avg_dp     += surf_dp[i]      
                else:
                    avg_temp   += surf_temp[i]
                    avg_rh     += surf_rh[i]
                    avg_pres   += surf_pres[i]
                    avg_ws     += surf_ws[i]
                    avg_wd     += surf_wd[i]
                    avg_dp     += surf_dp[i]