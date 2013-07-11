#!/usr/bin/env python
from os.path import splitext

from functools import partial

import yaml
from pysis import isis
#from pysis import IsisPool

from pysis.util import write_file_list
from pysis.labels import parse_file_label

from glob import iglob
import numpy as np

#This program applies the calibration and extinction coefficients 
# to the .cub files of each band of the ROLO dataset
# uncalibrated cubes are projected in ProjectionName = LunarAzimuthalEqualArea

# maptemplate map=ROLO_ortho.map projection=orthographic clat=0.0 clon=0.0 
# resopt=mpp resolution=7000 rngopt=user minlat=-90.0 maxlat=90.0 
# minlon=-90.0 maxlon=90.0

# Side note, to change this to run without multiprocessing you can just do:
import os
print 'ISIS3TESTDATA:', os.environ.get('ISIS3TESTDATA')
print 'ISISROOT:', os.environ.get('ISISROOT')

# ROLO images to use
rolo_set = 'mm2709'
rolo_subset = '04'
rolo_name = rolo_set + rolo_subset
base_dir = '/home/sbraden/ROLO/uncalibrated/'
rolo_dir = '/home/sbraden/ROLO/uncalibrated/'+ rolo_name
rolo_cal_dir = '/home/sbraden/ROLO/calibrated/'+ rolo_name

def prepare_image(image):
    # reproj map=ROLO_ortho.map
    isis.map2map(from_=image, map=base_dir+'ROLO_ortho.map', to=rolo_dir+'_ortho.cub', matchmap='true')
    # explode original uncalibrated cubes into new directory
	isis.explode(from_=rolo_dir+'_ortho.cub', to=rolo_dir+'/'+rolo_name)

def main():
    
	prepare_image(rolo_dir+'.cub')
	rolo_images = iglob(rolo_dir + '/*.cub') # all bands of rolo observation

	# open and read calibration parameters
	dtype = {
    	'names': ['band', 'julian_date', 'calibration_factor', 'extinction_factor'],
    	'formats': ['i4', 'f8', 'f8', 'f8']
	}
	parameters = np.loadtxt(rolo_dir +'_bnd_time_cal_ext.txt', dtype=dtype, delimiter=',')

	# The conversion of image pixels in DN to radiance (W/m^2 sr nm) 
	# is simply:radiance = DN * CALIBRATION * EXTINCTION
	ext_len = -len('.cub')

	i = 0 
	for image in rolo_images:
    	basename = image[:ext_len]
    	mult = parameters["calibration_factor"][i] * parameters["extinction_factor"][i]
    	isis.algebra(from_=rolo_dir+'/'+image, to=rolo_cal_dir+'/'+basename+'.cal.cub', operator='unary', A=mult)
    	i = i +1

	# remove bands with bad seeing: 4,6,9,13,16,19
	os.system('rm '+ rolo_cal_dir +'/band0004*.cub ')
	os.system('rm '+ rolo_cal_dir +'/band0006*.cub ')
	os.system('rm '+ rolo_cal_dir +'/band0009*.cub ')
	os.system('rm '+ rolo_cal_dir +'/band0013*.cub ')
	os.system('rm '+ rolo_cal_dir +'/band0016*.cub ')
	os.system('rm '+ rolo_cal_dir +'/band0019*.cub ')

if __name__ == '__main__':
    main()