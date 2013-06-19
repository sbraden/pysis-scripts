import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from pysis import isis
from argparse import ArgumentParser
from pysis import CubeFile


# masked area is white (255)
# the rest of the image is black (1)

# 100 mpp in x and y
# z direction is in meters
# each "voxel" is 100*100*1 = 10,000 m^3

def get_volume(topo_image, mask_image, args):
	# What does this shit here do?
    # Z = topo_image.data[0]
	# indicator = mask_image.data[0]
	# converting mask image to 1 byte per pixel of data
    # and making it True or False
    # then create it as a np.array (1D)
    mask = np.array(mask_image.convert('1').getdata(), dtype=bool)

    # img.data # np array with the image data
    #img.samples
    #img.line
    # scaled_data = img.apply_scaling() # apply scaling
    # mask = img.specials_mask() #apply a mask for special pixels
    # scaled_data[mask].sum() # this is the sum of all non-special pixels
	
    # this line gets the shape of the .cub file
    shape = topo_image.data[0].shape
    
    # this reshapes the 1D np.array to the shape of the .cub file
    mask = mask.reshape(shape)
    
    # set the area of the topo image which is not in the mask to 0
    topo_image.data[0][mask==False] = 0

    # Write out a .png at this point

    # Get the pixel area of the mask
    pixel_area = mask.sum()
    surface_area = pixel_area*int(args.pixelscale)*int(args.pixelscale) # surface_area in m^2
    print "area of mask in m^2:", surface_area
    print "area of mask in km^2:", surface_area*(10**-6)

    # "offset" = reference plane
    offset = int(args.referenceplane)
    # if min pixel is less than the offset : please barf
    min_pixel = topo_image.data[0][mask].min()
    mean_pixel = topo_image.data[0][mask].mean()
    std_pixel = topo_image.data[0][mask].std()
    print "mean_pixel value in topo image: ", mean_pixel
    print "std_pixel value in topo image: ", std_pixel
    assert abs(min_pixel) >= abs(offset) # if not true, throws AssertionError
    
    # set everything below the offset  to 0
    # this is if the topography falls below the offset
    # data = topo_image.data[0]
    # masked_data = data[mask]
    # bad_data = masked_data < offset
    # masked_data[bad_data] = offset

    # Get the sum of all the topo pixels in the mask
    volume = topo_image.data[0][mask].sum()

    volume = volume - (pixel_area * offset) # offset in dn
    # this should be volume -= to take care of the negative numbers in the elevations
    # really this works.
    area_per_pixel = 100 * 100 # units: m^2
    volume *= area_per_pixel

    print "volume in m^3:", volume
    print "volume in km^3:", volume*(10**-9) 

    return

# SARAH NOTES
#volume = sum of all pixels in mask
# if you sum all the pxiel in mask then you aren't 
# taking into account the reference plane.
# Trevor's way says take the reference plan and multipy it by the area
# and then you get the number that should be subtracted from the whole
# If you have negative numbers for the whole elevation, your sum is going to 
# be small, then the reference plane will be a "more negative" number.
# You will end up with sum = -400*10, reference plane = -1000*10. Then you will get
# -14000 as the "adjusted volume" Technically the real volume of a single pixel
# is 600 and the "real volume" is 6000. 

# GD case: offset
# minimum around the dome is -2212 m
# eastside mare avg is -2152 m
# westside highlands avg is -1950 m


def main():
    parser = ArgumentParser(description='Generate volume estimates using WAC DTM')
    parser.add_argument('image', metavar='cub',
                        help='the topo cube file(s) (.cub) to process')
    parser.add_argument('mask', metavar='cub',
                       help='the mask that outlines the roi for volume calculation')
    parser.add_argument('--pixelscale', '-p', default=100,
                       help='pixelscale of input images in meters per pixel')
    parser.add_argument('--referenceplane', '-r', default=0,
                       help='plane of reference for volume calculation at an elevation')
    args = parser.parse_args()

    # args.image
    # args.mask
    # args.pixelscale
    # args.referenceplane

    # open and read in WAC DTM cube file
    topo_image = CubeFile.open(args.image)
    # open and read in mask file (tif or png)
    mask_image = Image.open(args.mask)

    # Check to see that the files are the same size => this doesn't work
    #print "samples match:", topo_image.samples == mask_image.samples
    #print "lines match:", topo_image.lines == mask_image.lines

    get_volume(topo_image, mask_image, args)

if __name__ == '__main__':
    main()