#!/usr/bin/env python
#
# Sarah Braden
#
# Improved version of boxes.py
# Uses Pysis
#
# Enter in .csv file with lat, lon of a point
# 

# Some utilities
import sys, yaml, csv
import numpy as np
# Libs to read in the cub files
# import gdal

from pysis import isis
from pysis import CubeFile
from pysis.labels import parse_file_label

from argparse import ArgumentParser


def read_csv_data(filename):
    
    dtype = {
        "names": ['area_id', 'latitude', 'longitude', 'box_size_pixels'],
        "formats": ['S24', 'f8', 'f8', 'i4']
    }

    points = np.loadtxt(filename, dtype=dtype, delimiter=',', skiprows=1)

    return points


    # cube = parse_file_label(image.proj.cub)
    # label = cube['IsisCube']
    # print label
    # orbit = label['Archive']['OrbitNumber']
    # scale = label['Mapping']['PixelResolution']
    # time  = label['Instrument']['StartTime'].replace('T',' ')

    # isis.campt(from_=image, to=image.campt)
    # label = parse_file_label(image.campt)

    # points = label['GroundPoint']
    # clon  = points['PositiveEast360Longitude']
    # clat  = points['PlanetocentricLatitude']


def iround(x):
    """iround(number) -> integer
    Round a number to the nearest integer."""
    return int(round(x) - .5) + (x > 0)


def get_sample_line(filename, center_latitude, center_longitude):
    # call mappt to get the sample/line for the clat/clon from the projected image

    isis.mappt(from_=filename, to='sample_line.pvl', append='FALSE', type='ground',
                latitude=center_latitude, longitude=center_longitude)
    label = parse_file_label('sample_line.pvl')
    center_sample = label['Results']['Sample']
    center_line = label['Results']['Line']
    print center_sample
    print center_line

    # call getkey to get the sample/line
    #center_sample = os.popen('getkey from=sample_line.pvl grpname=Results keyword=sample').read()
    #center_line = os.popen('getkey from=sample_line.pvl grpname=Results keyword=line').read()

    return int(iround(center_sample)), int(iround(center_line)) #TODO: round, don't truncate


def main():
    parser = ArgumentParser(description='Basic input')
    parser.add_argument('csv_file',
                        help='csv input file with locations')
    parser.add_argument('cube_file',
                        help='cubefile to get values from')
    parser.add_argument('output_file',
                        help='.csv for data')
    args = parser.parse_args()

    image = CubeFile.open(args.cube_file) # pysis.cubefile.CubeFile
    print 'image samples = %i' % image.samples
    print 'image lines = %i' % image.lines
    # python is y, x in an array instead of isis x, y, thus take the transpose of the
    # image data array
    #image_data = image.apply_scaling()[0].T.astype(np.float64) # type = numpy.ndarray
    #image_data = image.apply_scaling()[0].T #applies scaling and Transposes
    #image_data = image.data[0].T # gets data and transposes
    image_data = image.apply_scaling()[0].T.astype(np.int)

    points = read_csv_data(args.csv_file)

    # Prepare our csv output file
    data_out = csv.writer(
        open(args.output_file, 'wb'),
        delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    data_out.writerow(['area_id', 'latitude', 'longitude', 'box_size_pixels', 'mean', 'stdev', 'boxsize'])

    # TODO: grab image resolution?

    # Calculate the stats for each region
    for i in range(0, len(points)):

        latitude = points['latitude'][i]
        longitude = points['longitude'][i]
        boxsize = points['box_size_pixels'][i]
        print 'boxsize = %i' % boxsize

        center_sample, center_line = get_sample_line(args.cube_file, latitude, longitude)
        print center_sample, center_line #debug

        # -1 is for the translation between isis and python 
        # isis starts at 0
        # python starts at 1

        if boxsize == 1:
            offset = 0
            area = image_data[center_sample-1, center_line-1] # isis => python pixel conversion
            print center_sample-1, center_line-1
            print 'pixel value = %i' % area
        else:
            offset = int(boxsize/2)
            x0, x1 = center_sample-offset , center_sample+offset
            y0, y1 = center_line-offset, center_line+offset
            area = image_data[x0-1:x1-1, y0-1:y1-1] # isis => python pixel conversion


        data_out.writerow([
            points['area_id'][i], points['latitude'][i], points['longitude'][i],
            area.mean(), area.std(), points['box_size_pixels'][i] ])

if __name__ == '__main__':
    main()