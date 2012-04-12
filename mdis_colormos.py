#!/usr/bin/env python
import re
from glob import iglob
from math import floor
from pysis.commands import isis
from pysis.util import write_file_list, file_variations
from pysis.labels import parse_file_label, parse_label

# Sarah Braden
# 4/3/2012
# Must use isis 3.3.1
# new pysis script to create color mosaics from MDIS color images
# double check projections with project log
# sort the images by resolution so that the lower res images are first in the list

FILTER = 'D'
mosaic_name = '%s_mdis_wac_mos.cub' % (FILTER)

content_re = re.compile(r'(Group.*End_Group)', re.DOTALL)
def get_pixel_scale(img_name):
    # special case see git repository
    output = isis.campt.check_output(from_=img_name)
    output = content_re.search(output).group(1) 
    pixel_scale = parse_label(output)['GroundPoint']['SampleResolution']
    return pixel_scale


def sort_images(images, f, reverse=False):
    """ Sort a list of images by a value
    
    Args:
        images: The list of images you want to sort.
        f: A function that extracts the value for sorting (not included)
        reverse: reverse the sorting order

    Returns:
        A new list with the sorted images.
    """
    images = [(f(img_name), img_name) for img_name in images]
    images.sort(reverse=reverse)
    images = [img_name for value, img_name in images]
    return images


def basic_img_proc(img_name):
    (cub_name, cal_name) = file_variations(img_name, ['.cub', '.cal.cub'])
    isis.mdis2isis(from_=img_name, to=cub_name, target='MERCURY')
    isis.spiceinit(from_=cub_name)
    isis.mdiscal(from_=cub_name, to=cal_name)


def main():
    images = iglob('*.IMG')
    
    isis.maptemplate(map='D_mdis_wac_eqr.map', projection='equirectangular',
        clon=0.0, clat=0.0, resopt='mpp', resolution=1000, rngopt='user', 
        minlat=-40.0, maxlat=40.0, minlon=0.0, maxlon=360.0)

    for img_name in images:
        (cub_name, cal_name, pho_name, trim_name, proj_name) = file_variations(img_name,
                        ['.cub', '.cal.cub', '.pho.cub', '.trim.cub', '.proj.cub'])
        #basic_img_proc(img_name)
        isis.photomet(from_=cal_name, to=pho_name, PHTNAME='HAPKEHEN', 
            Wh=0.215984749, Hh=0.075, B0=2.3, Theta=15.78892162,
            HG1=0.206649235, HG2=0.811417942, zerob0standard='false',
            NORMNAME='Albedo', Incref=30.0, Thresh=10E30, Incmat=0.0, Albedo=1.0)
        isis.trim(from_=pho_name, to=trim_name, left=10)
        isis.cam2map(from_=trim_name, to=proj_name, pixres='map', 
                     map='D_mdis_wac_eqr.map', defaultrange='map')

    # sort by resolution: output is .proj.cub
    images = iglob('*.trim.cub')
    sorted_images = sort_images(images, get_pixel_scale, reverse=True)
    
    ext_len = -len('.trim.cub')
    sorted_images = [img_name[:ext_len] + '.proj.cub'
                        for img_name in sorted_images]

    write_file_list('mosaic.list', sorted_images)
    isis.automos(fromlist='mosaic.list', mosaic=mosaic_name)
    # reproject the mosaic in sinusoidal projection
    #isis.map2map( projection='sinusoidal')
    #isis.stats(from_='sinusoidal_proj' to='sinu_stats.txt')


if __name__ == '__main__':
    main()
