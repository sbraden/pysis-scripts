# replaces:
# incemis.py
# LSratioIMG.py

# python script to take the lat, lon of all points on a ROLO image of the Moon
# and calculate the incidence and emission angle of those points
# ROLO image projection is 7 km/px orthographic
# samples = 491 (columns)
# lines = 467 (rows)
# isis starts at 1
# Sarah Braden
# 6 September 2011

import numpy as np
from matplotlib import pyplot as plt
import scipy

# MAIN TO-DO: Make the functions select the correct image_group

# "mm185801.band0008.calmapcrop.cub"
image_name = 'mm185801'

def compute_emission_angles(image_name, angle_dict, image_data):
    """ compute emission angles
    
    Args:
        image_name: which set of images do we want angles for?
        angle_dict: dictionary of angles for images
        image_data: numpy array of image data

    Returns:
        emission angles for every point in the image.
    """
    deltalat = np.radians(np.abs(dictionary[image_name]['selat'] - pix['lat']))
    deltalon = np.radians(np.abs(angle_dict[image_name]['selon'] - pix['lon']))
    emission = np.degrees(np.arccos(np.cos(deltalat) * np.cos(deltalon)))
    return emission

def compute_incidence_angles(image_name, angle_dict, image_data):
    """ compute incidence angles
    
    Args:
        image_name: which set of images do we want angles for?
        angle_dict: dictionary of angles for images
        image_data: numpy array of image data

    Returns:
        incidence angles for every point in the image.
    """
    deltalat = np.radians(np.abs(angle_dict[image_name]['SSlat'] - pix['lat']))
    deltalon = np.radians(np.abs(angle_dict[image_name]['SSlon'] - pix['lon']))
    incidence = np.degrees(np.arccos(np.cos(deltalat) * np.cos(deltalon)))
    return incidence


def write_image(value, filename):
    """ write values in array to an ascii image
    
    Args:
        value: value you want to make an image for
        filename: output filename for the image
    """
    # # python is ( line, sample )
    # baseimg = scipy.zeros((467,491))    # a 491x467 array of float zeros
    # # isis starts at 1, python starts at 0.
    # # when converting into isis, the python 0,0 becomes isis 1,1
    # # to fix this, we will subtract the sample, lines in the data table by 1
    # samples = pix["sample"]-1
    # lines = pix["line"]-1
    # i=0
    # print len(value)
    # for i in range(0,len(value)):
    #   baseimg[ lines[i] ][ samples[i] ] = value[i]

    baseimg = scipy.zeros(467 * 491)

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
    rolo_pix_data = np.loadtxt('rolo_s_l_lat_lon.csv', dtype=dtype, delimiter=',')

    dtype = {
        'names': ['imagename', 'phase', 'selat', 'selon', 'sslat', 'sslon', 'lsratioatSE'],
        'formats': ['S64', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8']
    }
    angle = np.loadtxt('rolo_angle_info.csv', dtype=dtype, delimiter=',')

    rolo_angle_dict = dict(zip(angle['imagename'], angle))

    emission = compute_emission_angles(image_name, rolo_angle_dict, rolo_pix_data)
    incidence = compute_incidence_angles(image_name, rolo_angle_dict, rolo_pix_data)

    # calculate Lommel-Seeliger factor for each point
    # L-S = cos(i) / ( cos(e) + cos(i) )
    LommelSeeliger = np.cos( np.radians(incidence) ) / ( np.cos( np.radians(emission) ) + np.cos( np.radians(incidence)))
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