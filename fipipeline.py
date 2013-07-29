#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Process a featured image.

Usage:
  fipipeline.py [--title=TITLE] [--caption=CAPTION] <images>...
  fipipeline.py -h | --help

Options:
  -h --help          Show this screen.
  --title=TITLE      The title of the post [default: New Title].
  --caption=CAPTION  A short caption for the post.

"""
import os
import yaml
from docopt import docopt

from pysis import isis
from pysis.util import write_file_list
from pysis.labels import parse_file_label

from darkroom import (
    Darkroom,
    Step,
    ImageList,
    TempImage,
    img_mapper,
    mapper,
    identity,
)

@img_mapper
def lronac2isis(img_from, img_to, **options):
    isis.lronac2isis(from_=img_from, to=img_to)

@identity
def spiceinit(image, **options):
    isis.spiceinit(from_=image)

@img_mapper
def lronaccal(img_from, img_to, **options):
    isis.lronaccal(from_=img_from, to=img_to)

@img_mapper
def trim(img_from, img_to, left=45, right=45, **options):
    isis.trim(from_=img_from, to=img_to, left=left, right=right)

@img_mapper
def project(img_from, img_to, **options):
    with img_from.make_child(ext='map') as mapfile:
        with img_from.make_child(ext='lis') as fromlist:
            write_file_list(fromlist, [img_from])

            isis.mosrange(
                fromlist   = fromlist,
                to         = mapfile,
                precision  = 2,
                projection = 'equirectangular'
            )

        isis.cam2map(
            from_  = img_from,
            to     = img_to,
            pixres = 'map',
            map    = mapfile
        )

def rename(image, ext, strip_ext=''):
    if name.endswith(trim_ext):
        name = name[:-len(trim_ext)]

    return name + ext

@mapper
def name_image(image, ext, strip_ext='', **options):
    if isinstance(image, TempImage):
        name = image.base
    else:
        name = image

    name = rename(name, ext, strip_ext)
    os.rename(image, name)

    if isinstance(image, TempImage):
        image.cleanup(propagate=True)

    return name

@identity
def fi_yaml(image, **options):
    cube = parse_file_label(image)
    label = cube['IsisCube']
    orbit = label['Archive']['OrbitNumber']
    scale = label['Mapping']['PixelResolution']
    time  = label['Instrument']['StartTime'].replace('T',' ')

    with TempImage(image, 'campt') as campt:
        isis.campt(from_=image, to=campt)
        label = parse_file_label(campt)

    points = label['GroundPoint']
    clon  = points['PositiveEast360Longitude']
    clat  = points['PlanetocentricLatitude']

    data = {
        ':release':    'YYYY-MM-DD 10:00:00.00 +00:00',
        ':title':      title,
        ':timestamp':  '%s +00:00' % time,
        ':orbit':      orbit,
        ':clat':       '%.3f&deg;' % clat,
        ':clon':       '%.3f&deg;' % clon,
        ':resolution': '%.2f m/pixel' % scale['value'],
        ':mode':       'Native',
        ':ptif':       str(image.tif),
        ':thumb':      str(image.png)
    }

    with open(rename(image, '.yml', '.proj.cub'), 'w') as fp:
        yaml.dump(data, fp, default_flow_style=False)

@identity
def fi_caption(image, caption, **options):
    template = '<p>{}</p><div>[NASA/GSFC/Arizona State University].</div>'

    with open(rename(image, '.caption', '.proj.cub'), 'w') as fp:
        fp.write(template.format(caption))

def main():
    opts = docopt(__doc__)

    pipeline = Darkroom([
        lronac2isis,
        spiceinit,
        lronaccal,
        trim,
        project,
        Step(name_image, ext='.proj.cub', strip_ext='.IMG'),
        Step(fi_yaml, title=opts['--title']),
        Step(fi_caption, caption=opts['--caption'] or ''),
    ])

    images = ImageList(opts['<images>'])
    pipeline.run(images)


if __name__ == '__main__':
    main()
