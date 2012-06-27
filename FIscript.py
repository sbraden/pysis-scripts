#!/usr/bin/env python
from os.path import splitext
from argparse import ArgumentParser

from functools import partial
from multiprocessing import Pool

import yaml
from pysis import isis
from pysis import IsisPool

from pysis.util import write_file_list
from pysis.labels import parse_file_label

class ImageName(str):
    def __getattr__(self, ext):
        return ImageName(self + '.' + ext)

    def __repr__(self):
        return '%s(%r)' %  (self.__class__.__name__, str(self))

def create_yml(image, title):
    """ This function generates a yml file with information.
    Args:
        image:
        title:
    """
    cube = parse_file_label(image.proj.cub)
    label = cube['IsisCube']
    print label
    orbit = label['Archive']['OrbitNumber']
    scale = label['Mapping']['PixelResolution']
    time  = label['Instrument']['StartTime'].replace('T',' ')

    isis.campt(from_=image, to=image.campt)
    label = parse_file_label(image.campt)

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

    with open(image.yml, 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)

def create_caption(image, caption):
    template = '<p>%s</p><div>[NASA/GSFC/Arizona State University].</div>'

    with open(image.caption, 'w') as caption_file:
        caption_file.write(template % caption)

def process_images(images, title, caption):
    """
        Gets passed "images", with multiple "image"
        the extensions are called "ext_set"
        the img_set has the imagename + ext_set
        look at named tuples for future reference
    """
    images = [ImageName(splitext(image)[0]) for image in images]
    
    with IsisPool() as isis_pool: 
        for image in images:
            isis_pool.lrocnac2isis(from_=image.IMG, to=image.cub)

    with IsisPool() as isis_pool: 
        for image in images:
            isis_pool.spiceinit(from_=image.cub)

    with IsisPool() as isis_pool: 
        for image in images:
            #lronaccal default is IOF calibration
            isis_pool.lronaccal(from_=image.cub, to=image.cal.cub)

    with IsisPool() as isis_pool: 
        for image in images:
            isis_pool.trim(from_=image.cal.cub, to=image.trim.cub,
                           left=45, right=45)

    with IsisPool() as isis_pool:
        for image in images:
            write_file_list(image.map.lis, [image.trim.cub])
            isis_pool.mosrange(fromlist=image.map.lis,
                               to=image.nac_eqr.map,
                               precision=2, projection='equirectangular')

    with IsisPool() as isis_pool: 
        for image in images:
            isis_pool.cam2map(from_=image.trim.cub, to=image.proj.cub,
                              pixres='map', map=image.nac_eqr.map)

    create_yml(image, title)
    create_caption(image, caption)

def process_image(image, title, caption):
    image = ImageName(splitext(image)[0])
    
    isis.lronac2isis.print_cmd(from_=image.IMG, to=image.cub)
    isis.lronac2isis(from_=image.IMG, to=image.cub)
    isis.spiceinit(from_=image.cub)

    #lronaccal default is IOF calibration
    isis.lronaccal(from_=image.cub, to=image.cal.cub)
    isis.trim(from_=image.cal.cub, to=image.trim.cub, left=45, right=45)

    write_file_list(image.map.lis, [image.trim.cub])
    isis.mosrange(fromlist=image.map.lis, to=image.nac_eqr.map,
                  precision=2, projection='equirectangular')

    isis.cam2map(from_=image.trim.cub, to=image.proj.cub,
                 pixres='map', map=image.nac_eqr.map)

    create_yml(image, title)
    create_caption(image, caption)

def is_file_list(filename):
    return filename[0] == '@'

def get_file_list(filename):
    with open(filename[1:]) as filelist:
        # Read in file and remove comments
        lines = [line.split('#')[0] for line in filelist     ]
        lines = [line.strip()       for line in lines        ]
        return  [line               for line in lines if line]

def get_images(image_arg):
    if is_file_list(image_arg):
        return get_file_list(image_arg)

    return [image_arg]

def validate_image(image):
    if image[-4:] != '.IMG':
        raise Exception('Image %s name must end in .IMG' % image)

def main():
    parser = ArgumentParser(description='Process a featured image')
    parser.add_argument('images', metavar='IMG', nargs='+',
                        help='the image file(s) (.IMG) to process')
    parser.add_argument('--title', '-t', default='New Title',
                       help='the title of the post')
    parser.add_argument('--caption', '-c', default='Short Caption.',
                       help='a short caption for the post')

    args = parser.parse_args()

    # FIscript.py @images.list
    # when you have a plural variable name you imply it is a list
    images = [img for img_arg in args.images for img in get_images(img_arg)]
    # Validation
    for image in images:
        validate_image(image)

    # Using pysis multiprocessing
    # process_images(images, args.title, args.caption)

    # Or probably a much nicer way for you to do things:
    # Curry the process_image (see http://docs.python.org/library/functools.html#functools.partial)
    pipeline = partial(process_image, title=args.title, caption=args.caption) 

    # And use the python built-in process pool because you're a big girl now
    # (see http://docs.python.org/library/multiprocessing.html#module-multiprocessing.pool)
    # try:
    #     pool = Pool()
    #     pool.map_async(pipeline, images)
    #     pool.close()
    #     pool.join()

    # except Exception as error:
    #     pool.terminate()
    #     raise error

    # Side note, to change this to run without multiprocessing you can just do:
    import os
    print 'ISIS3TESTDATA:', os.environ.get('ISIS3TESTDATA')
    print 'ISISROOT:', os.environ.get('ISISROOT')
    map(pipeline, images) # http://docs.python.org/library/functions.html#map

if __name__ == '__main__':
    main()
