#!/usr/bin/env python

'''
Take a number of cubes and make them into a cloud plot.

Note to self. You are suppose to run this in the directory 
with the files (TODO: fix this later)

TODO: write in a function to recognize when filenames are
too long for matplotlib to handle.
'''
import itertools
import os.path
import numpy as np
import pandas as pd
from pysis import isis
from glob import iglob
from pysis import CubeFile
from os.path import basename
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties


x1= 320
x2= 415

y1= 950
y2= 750

x = x1/x2
y = y1/y2

# Colors will be applyed to filters by filter in alphabetical ordear
colors = [
  'red',
  'blue',
  'green',
  'purple',
  'cyan',
  'magenta',
  'black',
  'darkorange',
  'burlywood',
  'lightgreen'
]

colorloop=itertools.cycle(colors) # using intertools!


def make_cloud_plot(image_list, color, groupname):
    '''   
    Just pass one of the image_list
    '''
    for img_name in image_list:
        roi_name = os.path.basename(img_name)[:-8]
        base_path = img_name[:-8]
        image1 = CubeFile.open(img_name) # pysis.cubefile.CubeFile
        wac_320 = image1.apply_numpy_specials()[0].T
        wac_360 = image1.apply_numpy_specials()[1].T
        wac_415 = image1.apply_numpy_specials()[2].T
        wac_566 = image1.apply_numpy_specials()[3].T
        image2 = CubeFile.open(base_path+'_clm.cub') # pysis.cubefile.CubeFile
        clm_750 = image2.apply_numpy_specials()[1].T
        clm_950 = image2.apply_numpy_specials()[3].T
        clm_415 = image2.apply_numpy_specials()[0].T

        xaxis = wac_415
        yaxis = wac_415/wac_566

        #plt.scatter(xaxis, yaxis, marker='.', label=(roi_name), c=color, edgecolor=color)
        coloriter = colorloop.next()
        plt.scatter(xaxis, yaxis, marker='.', label=(roi_name), c=coloriter, edgecolor=coloriter)


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
        print roi_name, np.mean(x_data), np.mean(y_data), np.std(x_data), np.std(y_data)
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
    totally rewrite this so that the function only does 1 thing,
    not two. Ideally the function should only differentiate between
    wac and clm files, not do math.
    '''
    image = CubeFile.open(source_dir+img_name) # pysis.cubefile.CubeFile

    if img_name[-7:-4] == 'wac':
        wac_320 = image.apply_numpy_specials()[0].T
        print wac_320
        wac_415 = image.apply_numpy_specials()[2].T
        # tell pandas to handle the very negative numbers
        wac_320_over_415 = wac_320/wac_415
        #print wac_320_over_415
        return img_name[-7:-4], wac_320_over_415
        #return img_name[-7:-4], wac_415
    elif img_name[-7:-4] == 'clm':
        clm_950 = image.apply_numpy_specials()[3].T
        clm_750 = image.apply_numpy_specials()[1].T
        clm_950_over_750 = clm_950/clm_750
        print clm_950
        # tell pandas to handle the very negative numbers
        return img_name[-7:-4], clm_950_over_750
        #return img_name[-7:-4], clm_750
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
        print img_name
        camera, ratio_array = clem_or_wac(img_name)
        index.append(basename(img_name[:-4]))
        data.append(ratio_array)
        print data

    print 'applied scaling and transposing'
    return pd.DataFrame(data, index=index)


def main():

    # Write a part to put image directories into "groups"
    source_dirs = [
        #'/home/sbraden/400mpp_15x15_clm_wac/mare/',
        '/home/sbraden/400mpp_15x15_clm_wac/pyro/',
        #'/home/sbraden/400mpp_15x15_clm_wac/imps/',
        #'/home/sbraden/400mpp_15x15_clm_wac/mare_immature/'
        ]

    for directory in source_dirs:
        
        print directory
        groupname = os.path.split(os.path.dirname(directory))[1]
        print groupname
        # read in LROC WAC images
        wac_img_list = iglob(directory+'*_wac.cub')
        # read in Clementine images
        clm_img_list = iglob(directory+'*_clm.cub')

        make_cloud_plot(wac_img_list, colorloop.next(), groupname)

    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(loc='upper left', fancybox=True, prop=fontP, scatterpoints=1)
    #plt.axis([0.70, 0.86, 0.90, 1.15],fontsize=14)
    #plt.axis([0.84, 0.96, 0.90, 1.20],fontsize=14)
    plt.xlabel('WAC 415 nm', fontsize=14)
    plt.ylabel('WAC 415/566 nm', fontsize=14)
    plt.savefig('lunar_roi_cloud_plot.png', dpi=300)
    plt.close()
        
    #make_cross_plot(wac_df, clm_df)

if __name__ == '__main__':
    main()
