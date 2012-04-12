#!/usr/bin/env python
from argparse import ArgumentParser
from pysis.commands import isis
from pysis.util import write_file_list, file_variations
from pysis.headers import parse_file_header


def process_img(img_name):
    (cub_name, cal_name, trim_name, proj_name) = file_variations(img_name,
        ['.cub', '.cal.cub', '.trim.cub', '.proj.cub'])

    isis.lronac2isis(from_=img_name, to=cub_name)
    isis.spiceinit(from_=cub_name)

    #lronaccal default is IOF calibration
    isis.lronaccal(from_=cub_name, to=cal_name) 
    isis.trim(from_=cal_name, to=trim_name, left=45, right=45)

    write_file_list('map.lis', glob='*.trim.cub')
    isis.mosrange(fromlist='map.lis', to='nac_eqr.map', precision=2,
        projection='equirectangular')

    mapping = parse_file_header('nac_eqr.map')['Mapping']
    clon = mapping['CenterLongitude']
    clat = mapping['CenterLatitude']

    isis.maptemplate(fromlist='map.lis', map='cam2map.map',
        projection='equirectangular', clon=clon, clat=clat,
        rngopt='calc', resopt='calc')

    isis.cam2map(from_=trim_name, to=proj_name, pixres='map', map='cam2map.map') 


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Process a featured image')
    arg_parser.add_argument('img_name', metavar='IMG', help='the image file (.IMG) to process')
    args = arg_parser.parse_args()

    process_img(args.img_name)
