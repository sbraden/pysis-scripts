# pysistools.py
from pysis.commands import isis
from pysis.util import write_file_list, file_variations
from pysis.labels import parse_file_label, parse_label


# TODO: make a even/odd function that will perform a command for both even
# and odd wac frames.

'''
pysistools or pyst
Module for often used functions while scripting using pysis.
To use: import pysistools as pyst
'''

def get_pixel_scale(img_name):
    '''
    Input image filename
    Rturns the pixel_scale (as a string?)
    '''
    output = isis.campt.check_output(from_=img_name)
    output = content_re.search(output).group(1) 
    pixel_scale = parse_label(output)['GroundPoint']['SampleResolution']
    return pixel_scale


def get_center_lat_lon(minlat, maxlat, minlon, maxlon):
    '''
    Input minimum and maximum latitude and longitude
    Returns center latitude and longitude
    '''
    center_lat = minlat + abs(maxlat - minlat)/2
    center_lon = minlon + abs(maxlon - minlon)/2
    return center_lat, center_lon
#def get_center_lat_lon(region): # old version
#    minlat, maxlat = region[0], region[1]
#    minlon, maxlon = region[2], region[3]


def read_in_list(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines

def create_mosaic(subname):
    os.system('ls '+subname+'*.proj.cub '+ subname+'*.proj.cub > proj.lis')
    os.system('automos fromlist=proj.lis mosaic='+subname+'.mos.cub')
    os.system('rm -f proj.lis') # CLEAN UP
    pass


def makemap(region, feature, scale, proj):
    '''
    Uses a set of latitude and longitude boundaries, a projection, and
    a scale to create a mapfile.
    '''
    clon = region[2]+abs(region[3]-region[2])/2
    clat = region[0]+abs(region[1]-region[0])/2
    isis.maptemplate(map=feature+'.map', 
                     projection=proj,
                     clat=clat,
                     clon=clon,
                     rngopt='user',
                     resopt='mpp'
                     scale=scale,
                     minlat=region[0],
                     maxlat=region[1],
                     minlon=region[2],
                     maxlon=region[3]
                     )
    pass


def makemap_freescale(region, feature, proj, listfile):
    '''
    Uses a set of latitude and longitude boundaries, a projection,
    and a list of images to calculate the image scale
    A mapfile is created
    '''
    clon = region[2]+abs(region[3]-region[2])/2
    clat = region[0]+abs(region[1]-region[0])/2
    isis.maptemplate(map=feature+'.map',
                     fromlist=listfile, 
                     projection=proj,
                     clat=clat,
                     clon=clon,
                     rngopt='user',
                     resopt='calc'
                     scale=scale,
                     minlat=region[0],
                     maxlat=region[1],
                     minlon=region[2],
                     maxlon=region[3]
                     )
    pass



def process_frames(frames, color, name, model, feature): 
    '''
    Processes WAC frames (uv or vis) into regionally constrained images
    LROWACCAL calibrates pixels to DN
    '''
    subname = name+'.'+color
    mapname = feature+'.map'

    for frame in frames:
        isis.spiceinit(from_='+frame+', 
                       spksmithed='true', 
                       shape='user', 
                       model=model
                       )
        isis.lrowaccal(from_='+frame+',
                       to='+frame+'.cal,
                       RADIOMETRIC=FALSE
                       )
        isis.cam2map(from_='+frame+'.cal,
                     to='+frame+'.proj,
                     map=mapname,
                     matchmap=true
                     )

    create_mosaic(subname)


def get_image_info(filename):
    '''
    Runs catlab and gets the requested information

    Input: full filename
    
    Returns: Dictionary
    '''
    os.system('catlab from='+filename+' to=catlab.pvl append=FALSE')
    str1 = 'getkey from=catlab.pvl objname=IsisCube'
    #v1.6
    version_id = os.popen(str1+' grpname=Archive keyword=ProductVersionId').read()
    exp_time = os.popen(str1+' grpname=Instrument keyword=ExposureDuration').read()
    fpa_temp = os.popen(str1+' grpname=Instrument keyword=MiddleTemperatureFpa').read()
    #2011-10-10T13:45:31.791 ISO formatted date
    start_time = os.popen(str1+' grpname=Instrument keyword=StartTime').read() 
    samples = os.popen(str1+' grpname=Dimensions keyword=Samples').read() 
    lines = os.popen(str1+' grpname=Dimensions keyword=Lines').read()
    bands = os.popen(str1+' grpname=Dimensions keyword=Bands').read()

    data = {'version_id': float(version_id[1:]),
            'exp_time': float(exp_time),
            'fpa_temp': float(fpa_temp),
            'start_time': start_time,
            'samples': samples,
            'lines': lines,
            'bands': bands
            }

    os.system('rm -f catlab.pvl') # CLEAN UP

    return data


def get_points_angles(filename):
    '''
    Runs campt and gets the requested information

    Input: full filename
    
    Returns: Dictionary
    ''' 
    os.system('campt from='+filename+' to=campt.pvl append=FALSE')
    str1 = 'getkey from=campt.pvl grpname=GroundPoint'

    subsolar_azimuth = os.popen(str1+' keyword=SubSolarAzimuth').read()
    subsolar_ground_azimuth = os.popen(str1+' keyword=SubSolarGroundAzimuth').read()
    solar_distance = os.popen(str1+' keyword=SolarDistance').read()
    
    data = {'subsolar_azimuth': float(subsolar_azimuth),
            'subsolar_ground_azimuth': float(subsolar_ground_azimuth),
            'solar_distance': float(solar_distance)
            }
    '''
    image_writer = csv.writer(image_datafile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    image_writer.writerow([name, start_time, exp_time, fpa_temp, subsolar_azimuth, subsolar_ground_azimuth, solar_distance])
    '''
    os.system('rm -f campt.pvl') # CLEAN UP

    return data