import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.patches as mpatches
import os.path
from pysis import isis
from argparse import ArgumentParser
from pysis import CubeFile
import pyfits

# TODO: make is so the script will read in either a .cub or a .fits file 

# TODO: make it so python will crop an image with NULL pixels
# see notes on python masks below
    # scaled_data = img.apply_scaling() # apply scaling
    # mask = img.specials_mask() #apply a mask for special pixels
    # scaled_data[mask].sum() # this is the sum of all non-special pixels

# TODO: make the projection default to sinusoidal

# TODO: Auto scale bar seems to be working

# TODO: Have the option to read in a .csv file instead of command line input

# http://matplotlib.org/api/artist_api.html

# Scale bar breaks at high latitudes (reproj to orthographic or sinusoidal?)
# or change input to degrees

def color_plot_2D(image, args):

    samples = image.samples
    print image.samples, image.lines

    # boxsize is in meters
    # scalebar_width must be in pixels
    # TODO: scalebar is broken now. Just grab scale from label
    #scalebar_width = (boxsize/5)/100 # 100 pixels = 10 km

    # An matplotlib.image.AxesImage instance is returned (plot1)
    # the 0 tells it to plot the first band only
    plot1 = plt.imshow(image.data[0])
    ax = plt.gca() # not sure what this does but it works

    # color bar properties
    cbar = plt.colorbar(plot1, orientation="vertical")
    cbar.set_label('Elevation (m)', fontsize=20)

    # Set the color map
    plot1.set_cmap('jet')
    plt.axis('off') # by turning the axis off, you make the grid disappear

    # Draw a box
    # this remains even after you turn the axes off
    # xy = 0.75*image.samples, 0.90*image.lines # upper left hand corner location
    #width, height = scalebar_width, scalebar_width/4
    #ax.add_patch(mpatches.Rectangle(xy, width, height, facecolor="black",
    #    edgecolor="white", linewidth=1))

    #text_x = xy[0] + width/2
    #text_y = xy[1] + height/2

    #plt.text(text_x, text_y, str((scalebar_width*100)/1000) +' km', fontsize=10, rotation=0.,
    #    horizontalalignment="center", verticalalignment="center", color='white',
    #    bbox = dict(boxstyle="square", edgecolor='black', facecolor='black'))

    #plt.draw()

    plt.savefig(args.outname + '.png', dpi=300)

    if args.contours == True:
        print 'CONTOURS IN PROGRESS'
        print image.samples, image.lines
        X = np.arange(0, image.samples, 1)
        Y = np.arange(0, image.lines, 1)
        X, Y = np.meshgrid(X, Y)
        Z = image.data[0]
        # N is number of levels for the contours
        N = 8
        interval = (Z.max() - Z.min()) / N
        ''' OVERRIDE '''
        #interval = (-1160 - -1569) / N

        # You can set negative contours to be solid instead of dashed:
        matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
        #plt.figure()
        print 'Z.max:', Z.max()
        print 'Z.min:', Z.min()
        print 'contour interval:', interval
        contour1 = plt.contour(X, Y, Z, N, colors='k') # negative contours will be dashed by default
        # plots labels to go with the contours
        #plt.clabel(contour1, fontsize=9, inline=1)
        plt.show()
        plt.axis('off')
        plt.savefig(args.outname + '_contours.png', dpi=300)
    pass


def color_topo_3D(image, args):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    Z = image.data[0]
    X = np.arange(0, image.samples, 1)
    Y = np.arange(0, image.lines, 1)
    X, Y = np.meshgrid(X, Y)
    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet,
        linewidth=0, antialiased=False)
    #ax.set_zlim(-1.01, 1.01)
    # how do I set azimuth and elevation? (-90 deg, -70 deg)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()
    plt.savefig(args.outname + '_3D.png', dpi=300)
    pass

def get_center_lat_lon():
    print "Enter min latitude (2 decimal places):"
    minlat = float(raw_input("> "))
    print "Enter max latitude (2 decimal places):"
    maxlat = float(raw_input("> "))
    print "Enter min longitude (2 decimal places):"
    minlon = float(raw_input("> "))
    print "Enter max longitude(2 decimal places):"
    maxlon = float(raw_input("> "))

    return minlat, maxlat, minlon, maxlon


def main():
    parser = ArgumentParser(description='Create plots for topo data')
    #parser.add_argument('image', metavar='cub',
    #                    help='the cube file(s) (.cub) to process, no NULL pixels')
    parser.add_argument('outname',
                        help='the output filename, no extension')
    parser.add_argument('GLD_slice', metavar='cub',
                        help='the WAC GLD100 slice to use (full path) (.cub)')
    parser.add_argument('--type', '-t', default='2D',
                       help='type of plot: 2D or 3D')
    parser.add_argument('--contours', '-c', default=True,
                       help='set to True for contour lines')
    parser.add_argument('--cinterval', '-i', default='10',
                       help='interval in meters for contour lines')
    args = parser.parse_args()


    minlat, maxlat, minlon, maxlon = get_center_lat_lon()

    center_lat = minlat + (maxlat - minlat)/2
    center_lon = minlon + (maxlon - minlon)/2
   
    # TODO: equirectangular is hardcoded at the moment
    # TODO: orthographic gives incorrect output... why?
    isis.maptemplate(map='wac_GLD100.map', projection='equirectangular', clat=center_lat,
        clon=center_lon, rngopt='user', resopt='mpp', resolution=100, 
        minlat=minlat, maxlat=maxlat, minlon=minlon, maxlon=maxlon)

    isis.map2map(from_=args.GLD_slice, map='wac_GLD100.map', to=args.outname+'.cub',
        matchmap='true')

    img = CubeFile.open(args.outname+'.cub')
    
    if args.type == '2D':
        color_plot_2D(img, args)

    if args.type == '3D':
        color_topo_3D(img, args)

    img.data # np array with the image data
    #img.samples
    #img.line


if __name__ == '__main__':
    main()
