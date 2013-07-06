# replaces:
# incemis.py
# LSratioIMG.py

# python script to take the lat, lon of all points on a ROLO image of the Moon
# and calculate the incidence and emission angle of those points
# ROLO image projection is 7 km/px orthographic
# samples = 491 (columns)
# lines = 467 (rows)

# Sarah Braden
# 6 September 2011

import numpy as np
from matplotlib import pyplot as plt
import scipy
import rolotools

# MAIN TO-DO: Make the functions select the correct image_group

# "mm185801.band0008.calmapcrop.cub"
image_name = 'mm185801'

def write_image(value, filename):
    """ write values in array to an ascii image
    
    Args:
        value: value you want to make an image for
        filename: output filename for the image
    """
    # python is (line, sample)
    # isis starts at 1, python starts at 0.
    # When converting into isis, the python 0,0 becomes isis 1,1
    # to fix this, we will subtract the sample, lines in the data table by 1

    baseimg = scipy.zeros(467 * 491) # a 491x467 array of float zeros

    lines = pix['line'] - 1
    samples = pix['sample'] - 1
    index = (491 * lines) + samples

    baseimg[index] = value
    # reshape is a special method for numpy arrays
    baseimg = baseimg.reshape((467, 491))

    # write the 2d array out as an ascii file that can be read in isis
    f = open(filename, 'w')
    np.savetxt(filename, baseimg)
    return


def main():

    # read in lat and lon from the ROLO data file
    # Filename,Sample,Line,PlanetocentricLatitude,PositiveEast180Longitude
    dtype = {
      'names': ['filename','sample','line','lat','lon'],
      'formats': ['S64', 'f8','f8', 'f8', 'f8']
    }
    # rolo_pix_data: numpy array of image data
    rolo_pix_data = np.loadtxt('rolo_s_l_lat_lon.csv', dtype=dtype, delimiter=',')

    dtype = {
        'names': ['imagename', 'phase', 'selat', 'selon', 'sslat', 'sslon', 'lsratioatSE'],
        'formats': ['S64', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8']
    }
    angle = np.loadtxt('rolo_angle_info.csv', dtype=dtype, delimiter=',')

    # rolo_angle_dict: dictionary of angles for images
    rolo_angle_dict = dict(zip(angle['imagename'], angle))

    subearthlat = rolo_angle_dict[image_name]['selat']
    subearthlon = rolo_angle_dict[image_name]['selon']
    subsolarlat = rolo_angle_dict[image_name]['sslat']
    subsolarlon = rolo_angle_dict[image_name]['sslon']
    lat, lon = rolo_pix_data['lat'], rolo_pix_data['lon']
    emission = rolotools.compute_emission(subearthlat, subearthlon, lat, lon)
    incidence = rolotoos.compute_incidence(subsolarlat, subsolarlon, lat, lon)

    # calculate Lommel-Seeliger factor for each point
    # L-S = cos(i) / ( cos(e) + cos(i) )
    LommelSeeliger = np.cos(np.radians(incidence))/(np.cos(np.radians(emission))+np.cos(np.radians(incidence)))
    # LS value at Sub Earth point
    LSsubearth = 0.4590 # I think I need to compute this for each image.
    # compute LS ratio for each point in image
    LSratio = LSsubearth / LommelSeeliger

    # write a function for generic ascii image writing
    # eventually this should be direct to isis (no ascii)
    write_image(emission, 'test_out_ema.ascii')
    write_image(incidence, 'test_out_inc.ascii')
    write_image(LSratio, 'test_out_LS_ratio.ascii')

if __name__ == '__main__':
    main()