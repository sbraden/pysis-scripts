#!/usr/bin/env python

'''
Take a number of cubes and make them into a cloud plot.
'''

from math import floor 
from pysis import isis
from pysis import CubeFile
from pysis.labels import parse_file_label, parse_label
import numpy as np
import pandas as pd
from glob import iglob

source_dir = '/home/sbraden/lunar_rois/matching_cubes/'


def clem_or_wac(img_name):
    '''
    Reads in image, reads extension,
    Python arrays are y, x instead of isis x, y => take the transpose of the
    image data array  
    '''
    image = CubeFile.open(source_dir+img_name) # pysis.cubefile.CubeFile
    if img_name[-7:-4] == 'wac':
        wac_320 = image.apply_scaling()[0].T #applies scaling and Transposes
        wac_415 = image.apply_scaling()[2].T
        wac_320_over_415 = wac_320/wac_415
        return img_name[-7:-4], wac_320_over_415

    elif img_name[-7:-4] == 'clm':
        clm_950 = image.apply_scaling()[3].T
        clm_750 = image.apply_scaling()[1].T
        clm_950_over_750 = clm_950/clm_750
        return img_name[-7:-4], clm_950_over_750
    else:
        print 'This is not a input cube that works with this script.'


def get_banddata(image_list):
    '''
    Takes in a list of images
    Performs math on selected bands
    Returns data in a pandas dataframe
    '''
    index = []
    data = []

    for img_name in image_list:
        basename = img_name[:-4]
        camera, ratio_array = clem_or_wac(img_name)
        index.append(basename)
        data.append(ratio_array)

    return pd.DataFrame(data, index=index)


def main():

    # read in WAC images
    wac_img_list = iglob(source_dir + '*_wac.cub')
    print wac_img_list
    # read in clementine images
    clm_img_list = iglob(source_dir + '*_clm.cub')

    wac_df = get_banddata(wac_img_list)
    clem_df = get_banddata(clm_img_list)
    # area.mean(), area.std()


if __name__ == '__main__':
    main()