from collections import deque
import dmtools
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from noise import snoise2
import numpy as np
from scipy.misc import imresize
from scipy.ndimage import imread, gaussian_filter
from scipy.spatial import Voronoi, voronoi_plot_2d

MAP_WIDTH = 2.
MAP_HEIGHT = 1.

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = IMAGE_WIDTH/2
EQUATOR_LEVEL = IMAGE_HEIGHT/2

CONTINENT_SCALE = 1.5
DETAIL = 0.5
DETAIL_SCALE = 2

OCEAN = 0
BARE = 1
TROPICAL_RAINFOREST = 2
TROPICAL_SEASONAL_FOREST = 3
SAVANNAH = 4
DESERT = 5
TEMPERATE_RAINFOREST = 6
TEMPERATE_FOREST = 7
WOODLAND = 8
GRASSLAND = 9
TAIGA = 10
TUNDRA = 11
SNOW = 12

PERLIN_OCTAVES = 10
PERLIN_PERSISTENCE = 0.7
PERLIN_LACUNARITY = 2.0

WIND_OCTAVES = 5

MAX_MOISTURE_TRAVEL = 100
MOISTURE_ELEVATION_PENALTY = 1

REDIST_STRENGTH = 1.5

ELEVATION_TEMP_CONTRIBUTION = 0.01

NGRID_X = IMAGE_WIDTH
NGRID_Y = NGRID_X/2

colors = \
{
    OCEAN: '#0000ff',
    BARE: '#cccccc'
}

class Region(object):
    def __init__(self, coords, vertices):
        self.coords = coords
        self.vertices = vertices
        self.elevation = -1
        self.vertex_elevations = [0]*len(vertices)
        self.water = False
        self.biome = BARE
        self.neighbours = []
        self.visited = False

def generate(water_level=0.15,
             seed=6,
             show_france=True):

    data_path = dmtools.get_data_path()
    
    # First, generate coastline.
    data = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH))
    for i in range(IMAGE_HEIGHT):
        for j in range(IMAGE_WIDTH):
            data[i,j] = generate_elevation(
                MAP_WIDTH*(float(j)/IMAGE_WIDTH),
                MAP_HEIGHT*(float(i)/IMAGE_HEIGHT),
                seed)
    
    elevation = np.copy(data)
    # rescale to be in [-1, 1]
    data = rescale(data)
    data = np.exp(data)-1
    data[data < water_level] = 0
    data[data > 0] = 1
    # add France
    if show_france:
        france_x = IMAGE_WIDTH*580/1024
        france_y = IMAGE_HEIGHT*440/512
        france_w = IMAGE_WIDTH*30/1024
        france = imread(data_path + "france.png", flatten=True)
        france_h = france.shape[1]*france_w/france.shape[0]
        france = imresize(france, (france_w, france_h))
        france[france > 0] = 1
        data[france_y:france_y+france_w, france_x:france_x+france_h] = france
    plt.imshow(data)
    plt.show()

    # Now generate mountains
    for i in range(IMAGE_HEIGHT):
        for j in range(IMAGE_WIDTH):
            elevation[i,j] += generate_elevation(
                    MAP_WIDTH*DETAIL_SCALE*(float(j)/IMAGE_WIDTH),
                    MAP_HEIGHT*DETAIL_SCALE*(float(i)/IMAGE_HEIGHT),
                    seed)
    elevation = np.exp(REDIST_STRENGTH*elevation)
    data = data * elevation
    plt.imshow(data)
    plt.show()

    # Now determine temperature
    scaled_elevation = imresize(data, (NGRID_Y, NGRID_X))
    temp = np.zeros((NGRID_Y, NGRID_X))
    scaled_equator_level = EQUATOR_LEVEL*NGRID_Y/IMAGE_HEIGHT
    max_dist_from_equator = max([scaled_equator_level,
        NGRID_Y-scaled_equator_level])
    min_latitude_temp = 0.1
    for i in range(NGRID_Y):
        temp[i,:] = 1-(abs(i-scaled_equator_level))/\
                float(max_dist_from_equator)
        temp[i,:] -= scaled_elevation[i,:]*ELEVATION_TEMP_CONTRIBUTION
    temp = rescale(temp)
    plt.imshow(temp)
    plt.show()

    # Wind
    wind = np.zeros((NGRID_Y, NGRID_X))
    for i in range(NGRID_Y):
        for j in range(NGRID_X):
            wind[i,j] = snoise2(float(i)/NGRID_X, float(j)/NGRID_Y,
                    octaves=WIND_OCTAVES, persistence=0.5,
                    lacunarity=PERLIN_LACUNARITY, base=seed,
                    repeatx=1)
    wind = rescale(wind)
    plt.imshow(wind)
    plt.show()

    # Moisture
    moisture = np.zeros((NGRID_Y, NGRID_X))
    for i in range(NGRID_Y):
        for j in range(NGRID_X):
            if scaled_elevation[i,j] > 0:
                d = 1
                y = j
                x = i
                for dist in range(MAX_MOISTURE_TRAVEL):
                    d += MOISTURE_ELEVATION_PENALTY*scaled_elevation[x,y]
                    if wind[x,y] > 0.5:
                        y -= 1
                    elif wind[x,y] < -0.5:
                        y += 1
                    else:
                        x += 1
                    x = x%NGRID_Y
                    y = y%NGRID_X
                    if scaled_elevation[x,y] < 1:
                        break
                moisture[i,j] = d
    moisture = 1 - np.divide(moisture, np.amax(moisture))
    # Smooth moisture map
    moisture = gaussian_filter(moisture, 2)
    plt.imshow(moisture)
    plt.show()

    # Biomes
    moisture = imresize(moisture, (IMAGE_HEIGHT, IMAGE_WIDTH))
    plt.imshow(moisture)
    plt.show()
    moisture = np.digitize(moisture, [0, 100, 150, 200, 255])-1
    moisture[moisture > 4] = 4
    plt.imshow(moisture)
    plt.show()
    temp = imresize(temp, (IMAGE_HEIGHT, IMAGE_WIDTH))
    plt.imshow(temp)
    plt.show()
    temp = np.digitize(temp, [0, 100, 140, 255])-1
    temp[temp > 2] = 2
    plt.imshow(temp)
    plt.show()

    biomes = [
        [BARE, TUNDRA, TAIGA, SNOW, OCEAN],
        [GRASSLAND, WOODLAND, TEMPERATE_FOREST, TEMPERATE_RAINFOREST, OCEAN],
        [DESERT, SAVANNAH, TROPICAL_SEASONAL_FOREST, TROPICAL_RAINFOREST, OCEAN]
        ]
    img = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH))
    for i in range(IMAGE_HEIGHT):
        for j in range(IMAGE_WIDTH):
            img[i,j] = biomes[temp[i,j]][moisture[i,j]]
    plt.imshow(img)
    plt.show()
   
def rescale(array):
    array -= (np.amin(array))
    array /= np.amax(array)
    array = 2*array - 1
    return array
    
def generate_elevation(x, y, seed=0):
    e = 0
    e += DETAIL*snoise2(CONTINENT_SCALE*x, CONTINENT_SCALE*y,
        octaves=PERLIN_OCTAVES,
        persistence=PERLIN_PERSISTENCE, lacunarity=PERLIN_LACUNARITY,
        base=seed, repeatx=MAP_WIDTH*CONTINENT_SCALE)
    return e

def generate_mountains(region, dir, det, dropoff, noise):
    regions = region.neighbours
    for other_region in regions:
        new_dir = np.asarray(other_region.coords)-np.asarray(region.coords)
        closeness = np.abs(np.dot(dir, new_dir))
        mountain_prob = closeness*det
        noise_var = noise*np.random.randn()
        if np.random.uniform() < mountain_prob:
            # continue with mountain
            other_region.elevation = region.elevation + noise_var
        else:
            other_region.elevation = dropoff*region.elevation + noise_var
        if other_region.elevation > 1:
            other_region.elevation = 1

def draw(regions):
    for region in regions:
        p = Polygon(region.vertices,
            facecolor=str(region.elevation) if region.biome is BARE
                else colors[region.biome],
            edgecolor='none')
        plt.gca().add_patch(p)
    plt.xlim([0, MAP_WIDTH])
    plt.ylim([0, MAP_HEIGHT])
    plt.show()
