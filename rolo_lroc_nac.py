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
# pysis script to project ROLO data to LROCNAC footprints 
# and get data

# ROLO images to use
rolo_observations = ['mm185801', 'mm185802', 'mm185803']

# this line needed to get info from isis.campt
content_re = re.compile(r'(Group.*End_Group)', re.DOTALL)

def get_pho_angles(img_name):    
        output = isis.campt.check_output(from_=img_name)
        output = content_re.search(output).group(1) 
        phase_angle = parse_label(output)['GroundPoint']['Phase']
        incidence_angle = parse_label(output)['GroundPoint']['Incidence']
        emission_angle = parse_label(output)['GroundPoint']['Emission']
        return phase_angle, incidence_angle, emission_angle


def project_rolo(rolo_observation, img_name):
    """" Reproject ROLO data onto LROC NAC footprints

    Args:
        rolo_observation: The rolo_observation that the images are from.
        img_name: The LROC NAC image that the ROLO data is reprojecting to.
    """
    rolo_images = iglob('/home/sbraden/data/ROLO/' + rolo_observation + '/*.cub')
    ext_len = -len('.IMG')
    no_ext = img_name[:ext_len]
    for rolo_name in rolo_images:
        isis.map2map(from_=rolo_name, to=no_ext+rolo_name, 
                    map='nac_eqr.map', pixres='mpp', 
                    resolution=7000, interp='nearestneighbor', 
                    defaultrange='map')

def main():
    images = iglob('*.IMG')
    
    pho_angles = [(img_name, get_pho_angles(img_name)) for img_name in images]

    for img_name in images:
        (cub_name, trim_name, proj_name) = file_variations(img_name,
            ['.cub', '.trim.cub', '.proj.cub'])

        isis.lronac2isis(from_=img_name, to=cub_name)
        isis.spiceinit(from_=cub_name)
        isis.trim(from_=cal_name, to=trim_name, left=45, right=45)

        write_file_list('map.lis', glob='*.trim.cub')
        isis.mosrange(fromlist='map.lis', to='nac_eqr.map', precision=2,
            projection='equirectangular')

        for i in rolo_observation
            project_rolo(rolo_observation[i], img_name)


    #mapping = parse_file_header('nac_eqr.map')['Mapping']
    #clon = mapping['CenterLongitude']
    #clat = mapping['CenterLatitude']
    #isis.cam2map(from_=trim_name, to=proj_name, pixres='map', map='nac_eqr.map') 

if __name__ == '__main__':
    main()