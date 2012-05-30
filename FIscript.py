#!/usr/bin/env python
from argparse import ArgumentParser
from pysis.commands import isis
from pysis.util import write_file_list, file_variations
from pysis.labels import parse_file_label, parse_label
import yaml

# add Pysis pool and multiple file processing?
# dictionary literals

def create_yml(img_name):
    """ This function generates a yml file with information.
    Args:
        img_name
    """

    label = parse_file_label(img_name)
    orbit = label['Archive']['OrbitNumber']
    scale = label['Mapping']['PixelResolution']
    clon  = label['Mapping']['PreciseCenterLongitude']
    clat  = label['Mapping']['PreciseCenterLatitude']
    time  = label['Instrument']['StartTime'].replace('T',' ')

    data = {
        ':release':   'YYYY-MM-DD 10:00:00.00 +00:00',
        ':title':     'New Title',
        ':timestamp': '%s +00:00' % time,
        ':orbit':     orbit,
        ':clat':      '%.3f&deg;' % clat,
        ':clon':      '%.3f&deg;' % clon,
        'resolution': '%.2f m/pixel' % scale,
        ':mode':      'Native',
        ':ptif':      '%s.tif' % img_name,
        ':thumb':     '%s.png' % img_name
    }

    yaml.dump(open(img_name+'.yml', 'w'), data)


def create_caption(img_name):
    textstr = '<p>Short Caption.</p> <div>[NASA/GSFC/Arizona State University].</div>'
    with open(img_name+'.caption', 'w') as caption_file:
        caption_file.write(textstr)


def get_clatlon(map_file):
    mapping = parse_file_header(map_file)['Mapping']
    clon = mapping['CenterLongitude']
    clat = mapping['CenterLatitude']
    return clon, clat


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

    clon, clat = get_clatlon('nac_eqr.map')

    isis.maptemplate(fromlist='map.lis', map='cam2map.map',
        projection='equirectangular', clon=clon, clat=clat,
        rngopt='calc', resopt='calc')

    isis.cam2map(from_=trim_name, to=proj_name, pixres='map', map='cam2map.map')

    create_yml(proj_name)
    create_caption(proj_name)


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Process a featured image')
    arg_parser.add_argument('img_names', metavar='IMG', help='the image file (.IMG) to process', numargs='+')
    args = arg_parser.parse_args()

    img_names = []
    for img_name in args.img_names:
        if img_name[0] == '@':
            with open(img_name[1:]) as f:
                img_names.extend([line.strip() for line in f if line.strip()])
        else:
            img_names.append(img_name)

    process_img(args.img_names)

    # FIscript.py @images.list
    # when you have a plural variable name you imply it is a list
