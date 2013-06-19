#!/usr/bin/env python
import os
import csv
import math

from pysis import isis
from pysis import CubeFile

from argparse import ArgumentParser
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate


# Sarah Braden
# Feb. 2013
# input image must be a square?

def read_csv_data(filename):
    
    dtype = {
        "names": ['image_filename', 'start_sample', 'start_line', 'end_sample', 'end_line', 'id'],
        "formats": ['S30', 'i4', 'i4', 'i4', 'i4', 'S16']
    }

    # TODO: also input image resolution?

    parameters = np.loadtxt(filename, dtype=dtype, delimiter=',', skiprows=1)

    return parameters


def get_lines(i, parameters):

    x0, y0 = parameters['start_sample'][i], parameters['start_line'][i] # SWITCH?
    x1, y1 = parameters['end_sample'][i], parameters['end_line'][i] # SWITCH?

    line_length = int( math.sqrt( abs(x0-x1)**2 + abs(y0-y1)**2 ) )
    print line_length # DEBUG
    # np.linspace returns evenly spaced numbers over a specified interval
    x, y = np.linspace(x0, x1, line_length), np.linspace(y0, y1, line_length)

    return x, x0, x1, y, y1, y0


def get_profile(image_data, x, y):

    # Extract the values along the line, using cubic interpolation
    # zi = scipy.ndimage.map_coordinates(image_data[0], np.vstack((x,y)))

    # Extract the values along the line, using nearest neighbor interpolation
    # TODO: is this doing it correctly???? 
    zi = image_data[x.astype(np.int), y.astype(np.int)] #

    return zi # TODO: get a better name for this


def main():
    parser = ArgumentParser(description='Basic input')
    #parser.add_argument('rootpath', 
    #    help='the root path with the directory of images')
    parser.add_argument('csv_file',
                        help='csv input file with profile parameters')
    parser.add_argument('--interp_type', '-i',
                        help='nearest_neighbor or cubic')
    args = parser.parse_args()

    parameters = read_csv_data(args.csv_file)

    print parameters.size # DEBUG

    nadir_image = CubeFile.open('M177514916_2m_crop.cub')
    nadir_image_data = nadir_image.apply_scaling()[0].T.astype(np.float64)

    for i in range(0, parameters.size):

        image = CubeFile.open(parameters['image_filename'][i]) # pysis.cubefile.CubeFile
        # image_size = image.samples

        # in python arrays are [line, sample] instead of [sample, line]
        # Transpose to fix:
        # image_data = image.apply_scaling()[0].T.astype(np.float64) # type = numpy.ndarray
        image_data = image.apply_numpy_specials()[0].T.astype(np.float64)
        print np.min(image_data), np.max(image_data), np.mean(image_data)
        print parameters['image_filename'][i]

        x, x0, x1, y, y1, y0 = get_lines(i, parameters)

        zi = get_profile(image_data, x, y)

        x,y = np.round(x).astype(np.int), np.round(y).astype(np.int)
        v = np.max(image_data)

        from itertools import combinations_with_replacement

        for dx, dy in combinations_with_replacement(xrange(-5, 5), 2):
            image_data[x+dx, y+dy] = v
            if dx == dy:
                continue

            image_data[x+dy, y+dx] = v\

        #-- Plot...

        
        # plt.subplots returns fig, ax
        # fig is the matplotlib.figure.Figure object
        # ax can be either a single axis object or an array of axis objects 
        # if more than one subplot was created. The dimensions of the resulting 
        # array can be controlled with the squeeze keyword, see above.

        plt.figure(0)

        dem_axis = plt.subplot2grid((2,2), (0,0), colspan=1)
        image_axis = plt.subplot2grid((2,2), (0,1), colspan=1)
        profile_axis = plt.subplot2grid((2,2), (1,0), colspan=2)

        # fig, axes = plt.subplots(nrows=2)
        dem_axis.imshow(image_data.T) # Transpose done here
        dem_axis.plot([x0, x1], [y0, y1], 'w-')
        dem_axis.xaxis.tick_top()
        dem_axis.set_xlabel('samples')
        dem_axis.xaxis.set_label_position('top')
        dem_axis.set_ylabel('lines')
        # print dem_axis.get_ylim() # (2000.0, -500.0)
        # print dem_axis.get_xlim() # (-500.0, 2000.0)
        dem_axis.set_ylim(image.lines, 0)
        dem_axis.set_xlim(0, image.samples)
        print dem_axis.get_ylim() # debug
        print dem_axis.get_xlim() # debug

        image_axis.imshow(nadir_image_data.T, cmap='gray') # Transpose done here
        # cmap ='gray' looks washed out...'
        image_axis.plot([x0, x1], [y0, y1], 'r-')
        image_axis.set_ylim(nadir_image.lines, 0)
        image_axis.set_xlim(0, nadir_image.samples)
        image_axis.set_title('image')

        # IMAGE xy SCALE 
        image_scale = 2 # units = meters per pixel

        # Create x axis vector to put plot in units of meters
        xi = np.arange(0, len(zi)*image_scale, image_scale)

        profile_axis.plot(xi, zi)

        profile_axis.set_xlabel('meters', fontsize=14)
        profile_axis.set_ylabel('elevation [meters]', fontsize=14)
        profile_axis.set_title('profile ' + parameters['id'][i], fontsize=14)

        profile_axis.axis('tight')
        # TODO: set aspect ratio for the topo profiles
        # axes[1].set_aspect('equal')
        profile_axis.set_aspect(5)



        plt.show()
        plt.savefig(str(i) + 'name.png', dpi=200)


if __name__ == '__main__':
    main()