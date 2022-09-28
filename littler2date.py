#######################################
#
# Graham Moss
# 07/01/2021
# graham.moss@umconnect.umt.edu
# :)
#
#######################################
# .Littler to obs date format.
'''
The purpose of this program is to take in a variety of
littler observational nudging files and orders them in
preparation for input into the OBSGRID program.
This program also takes radiosonde data that is in single
line observations and moves them into groups of 5 observations.
This is done because OBSGRID will treat single sounding data
points as surface data which is bad. File names must be in the
format: '####hhmm_MMDDYY******.littler'
This program will open files 3 hours before an observational point,
but will only write data that is 3 minutes before or after an observational
point.
'''
# Import modules
import datetime as dt
import numpy as np
import sys, os
import scipy.stats as ss

# Define functions
def get_time(date):
	year 	= int(date[0:4])
	month 	= int(date[4:6])
	day 	= int(date[6:8])
	hour 	= int(date[8:10])
	minute  = int(date[10:12])
	second  = int(date[12:14])
	return dt.datetime(year, month, day, hour, minute, second)
	
def get_sonde_time(date):
	hour 	= int(date[4:6])
	minute  = int(date[6:8])
	month 	= int(date[9:11])
	day 	= int(date[11:13])
	year 	= int('20' + date[13:15])
	return dt.datetime(year, month, day, hour, minute)

# User input
print(sys.argv)
if len(sys.argv) < 5:
	print('### ERROR ###\n' \
	      'Must have at least 4 arguments\n' \
	      'Start date = YYYYMMDDhhmmss\n' \
	      'End date = YYYYMMDDhhmmss\n' \
	      'In file directory = path_to_directory\n' \
	      'Save file directory = path_to_directory/\n' \
	      'optional: time_interval = int, default = 10800\n' \
	      '### ERROR Exiting ###')
	sys.exit()
startdate 	= sys.argv[1]
enddate 	= sys.argv[2]
# Note that need a met_em file for every desired time
if len(sys.argv) == 6:
	time_interval = int(sys.argv[5])
else:
	time_interval = 10800 # 3 hours
directory = sys.argv[3]
writedir = sys.argv[4]

# conversions based on times
sd = get_time(startdate)		# Start time
ed = get_time(enddate)			# End time
ti = dt.timedelta(seconds = time_interval)	# time delta
hr = dt.timedelta(seconds = 3600)	# 1 hour time delta
mi = dt.timedelta(seconds = 60)	# 1 minute time delta
ct = sd				# current time = st

# Loop over times 
while ct <= ed:
	print('Writing file:', ct)
	lfiles = []	# list of file names
	ltimes = []	# list of file times

	# This loop populates the 2 lists defined above.
	for entry in os.scandir(directory):
		if os.path.basename(entry)[-7:] == 'littler':
			if os.path.basename(entry)[:4] == '____':
				lfiles.append(entry.path)
				print('opened file: ', entry.path)
			else:
				t = get_sonde_time(os.path.basename(entry))
				if t <= (ct + 30*mi) and t >= (ct - 3*hr):
					lfiles.append(entry.path)
					print('opened file: ', entry.path)
					ltimes.append(t)
	
	num = len(lfiles) # number of open files
	ofiles = [*range(num)] 
	for n in ofiles: ofiles[n] = 'o' + str(n)
	counters = []
	
	# open files into memory
	for i in range(num):
		counters.append(0)
		ofiles[i] = open(lfiles[i],'r')
		
	# open write file obs:YYYY_MM_DD_hh
	wfile = open(writedir + 'obs:' + str(ct)[:10] + '_' + str(ct)[11:13], 'w')
	content = list(map(chr, range(97, 97+num)))
	ldates = [] # list of current working file time for each file
	end_counts = [] # number of lines in each file
	source = []	# source to check if radiosonde
	
	# this loop populates above lists
	for j in range(num):
		content[j] = ofiles[j].readlines()
		ofiles[j].close()
		ldates.append(get_time(content[j][counters[j]][326:340]))
		end_counts.append(len(content[j]))
		source.append(content[j][0][160:200].strip())
	print('source = ',source)
	
	# Starting one time interval behind the time and going to 30 minutes after
	timex = ct - ti
	while timex <= ct + dt.timedelta(seconds=1800):
		# find which file is oldest in working time
		rd = ss.rankdata(ldates)
		whr = np.where(rd == min(rd))[0][0] # whr is index of working file for loop
		timex = ldates[whr] # current time of file
		if timex.timestamp() % 3600 == 0: # print hourly for diagnostics
			print('file time calculation = ',timex)
		#print(*content[whr][counters[whr]:counters[whr]+4])
		if source[whr] == 'balloon': # radiosonde balloons get special treatment
			# if in right time range write next five data points with one header and tail
			if timex >= ct - dt.timedelta(seconds=1800) and timex <= ct + dt.timedelta(seconds=1800):
				c = 0
				for line in content[whr][counters[whr]:counters[whr]+5*4]:
					if c == 0:
						wfile.write(line[:228] + ' 5' + line[230:])
					elif c == 5*4-2:
						wfile.write(line)
					elif c == 5*4-1:
						wfile.write(line[:5] + ' 5' + line[7:])
					elif c % 4 - 1 == 0:
						wfile.write(line)
					c += 1
			counters[whr] += 5*4 # add counters
			# if reached the end of file remove working data at whr index
			if counters[whr]+5*4 >= end_counts[whr]:
				num -= 1
				if num == 0:
					break
				print('removed ', ofiles[whr])
				content.pop(whr)
				ofiles.pop(whr)
				ldates.pop(whr)
				counters.pop(whr)
				end_counts.pop(whr)
				source.pop(whr)
				rd = ss.rankdata(ldates)
				whr = np.where(rd == min(rd))[0][0]
			ldates[whr] = get_time(content[whr][counters[whr]][326:340])
		####################################################################
		# for all other one data point files write data in chrono order.
		else:
			if timex >= ct - dt.timedelta(seconds=1800) and timex <= ct + dt.timedelta(seconds=1800+time_interval):
				for line in content[whr][counters[whr]:counters[whr]+4]:
					wfile.write(line)
			counters[whr] += 4
			# remove index whr if reached end of file.
			if counters[whr]+4 >= end_counts[whr]:
				num -= 1
				if num == 0:
					break
				print('removed ', ofiles[whr])
				content.pop(whr)
				ofiles.pop(whr)
				ldates.pop(whr)
				counters.pop(whr)
				end_counts.pop(whr)
				source.pop(whr)
				rd = ss.rankdata(ldates)
				whr = np.where(rd == min(rd))[0][0]
			ldates[whr] = get_time(content[whr][counters[whr]][326:340])
	
	ct += ti # continue onto the next time interval
