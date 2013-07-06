#!/usr/bin/env python

'''
Take a number of cubes and make them into a cloud plot.
'''
import itertools
import numpy as np
import pandas as pd
from pysis import isis
from glob import iglob
from pysis import CubeFile
from os.path import basename
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties


source_dir = '/home/sbraden/lunar_rois/matching_cubes/'

# Colors will be applyed to filters by filter in alphabetical ordear
colours = [
  'red',
  'blue',
  'green',
  'burlywood',
  'cyan',
  'magenta',
  'yellow',
  'black',
  'darkorange',
  'purple',
  'lightgreen'
]

colorloop=intertools.cycle(colors) # using intertools!


def make_cloud_plot(wac_df, clm_df):
    '''
    x = 320/415
    y = 950/750
    '''

    for index_name in wac_df.index:
        roi_name = index_name[:-4]
        x = wac_df.loc[index_name].values
        y = clm_df.loc[roi_name+'_clm'].values
        plt.scatter(x[0], y[0], marker='o', label=(roi_name), 
            c=colorloop.next())

    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(loc='lower right', fancybox=True, prop=fontP, scatterpoints=1)
    plt.xlabel('320/415 nm WAC ratio', fontsize=14)
    plt.ylabel('950/750 nm CLEM ratio', fontsize=14)
    plt.savefig('lunar_roi_cloud_plot.png', dpi=300)
    plt.close()


def make_cross_plot(wac_df, clm_df):
    '''
    x = 320/415
    y = 950/750
    '''

    for index_name in wac_df.index:
        roi_name = index_name[:-4]
        x = wac_df.loc[index_name].values
        y = clm_df.loc[roi_name+'_clm'].values
        x_data = np.ma.masked_array(x[0],np.isnan(x[0]))
        y_data = np.ma.masked_array(y[0],np.isnan(y[0]))
        plt.errorbar(np.mean(x_data), np.mean(y_data), xerr=np.std(x_data),
            yerr=np.std(y_data), marker='o', label=(roi_name), 
            c=colorloop.next())

    rois_rough = pd.read_csv('/home/sbraden/imps_ratio_rough.csv', index_col=0)
    rois_mare = pd.read_csv('/home/sbraden/imps_ratio_mare.csv', index_col=0)

    for roi_name in rois_rough.index:
        ratio = rois_rough.loc[roi_name].values
        plt.scatter(ratio[1], ratio[0], marker='s', c='blue')
    
    for roi_name in rois_mare.index:
        ratio = rois_mare.loc[roi_name].values
        plt.scatter(ratio[1], ratio[0], marker='s', c='red')

    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(loc='lower right', prop=fontP, numpoints=1)
    plt.xlabel('320/415 nm WAC ratio', fontsize=14)
    plt.ylabel('950/750 nm CLEM ratio', fontsize=14)
    plt.savefig('lunar_roi_cross_plot.png', dpi=300)
    plt.close()


def clem_or_wac(img_name):
    '''
    Reads in image, reads extension,
    Python arrays are y, x instead of isis x, y => take the transpose of the
    image data array  
    '''
    image = CubeFile.open(source_dir+img_name) # pysis.cubefile.CubeFile

    if img_name[-7:-4] == 'wac':
        wac_320 = image.apply_numpy_specials()[0].T
        wac_415 = image.apply_numpy_specials()[2].T
        # tell pandas to handle the very negative numbers
        wac_320_over_415 = wac_320/wac_415
        return img_name[-7:-4], wac_320_over_415
    elif img_name[-7:-4] == 'clm':
        clm_950 = image.apply_numpy_specials()[3].T
        clm_750 = image.apply_numpy_specials()[1].T
        clm_950_over_750 = clm_950/clm_750
        # tell pandas to handle the very negative numbers
        return img_name[-7:-4], clm_950_over_750
    else:
        print 'This is not a input cube that works with this script.'


#applies scaling and Transposes

def get_banddata(image_list):
    '''
    Takes in a list of images
    Performs math on selected bands
    Returns data in a pandas dataframe
    '''
    index = []
    data = []

    for img_name in image_list:
        camera, ratio_array = clem_or_wac(img_name)
        index.append(basename(img_name[:-4]))
        data.append(ratio_array)

    return pd.DataFrame(data, index=index)


def main():

    # read in WAC images
    wac_img_list = iglob('*_wac.cub')
    print wac_img_list
    # read in clementine images
    clm_img_list = iglob('*_clm.cub')

    wac_df = get_banddata(wac_img_list)
    print wac_df # debug
    clm_df = get_banddata(clm_img_list)
    print clm_df # debug
    make_cloud_plot(wac_df, clm_df)
    make_cross_plot(wac_df, clm_df)

if __name__ == '__main__':
    main()
