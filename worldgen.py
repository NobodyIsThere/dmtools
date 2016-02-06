from collections import deque
import cPickle as pickle
import dmtools
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from noise import snoise2
import numpy as np
import os.path
from scipy.misc import imresize
from scipy.ndimage import imread, gaussian_filter
from scipy.spatial import Voronoi, voronoi_plot_2d

MAP_WIDTH = 2.
MAP_HEIGHT = 1.

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = IMAGE_WIDTH/2
EQUATOR_LEVEL = IMAGE_HEIGHT/4

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

SHADOW_STRENGTH = 2

biome_colours = {
    OCEAN: [0, 0, 153],
    BARE: [50, 50, 50],
    TROPICAL_RAINFOREST: [0, 153, 0],
    TROPICAL_SEASONAL_FOREST: [102, 153, 0],
    SAVANNAH: [255, 255, 153],
    DESERT: [255, 255, 102],
    TEMPERATE_RAINFOREST: [51, 153, 51],
    TEMPERATE_FOREST: [0, 102, 0],
    WOODLAND: [51, 102, 0],
    GRASSLAND: [255, 204, 0],
    TAIGA: [0, 51, 0],
    TUNDRA: [102, 51, 0],
    SNOW: [255, 255, 255]
}

PERLIN_OCTAVES = 10
PERLIN_PERSISTENCE = 0.7
PERLIN_LACUNARITY = 2.0

WIND_OCTAVES = 5

MAX_MOISTURE_TRAVEL = 100
MOISTURE_ELEVATION_PENALTY = 1

REDIST_STRENGTH = 1.5

ELEVATION_TEMP_CONTRIBUTION = 0.01

NGRID_X = 1024
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
    generate_coastline(data_path, water_level, show_france, seed)
    generate_elevation(data_path, seed)
    generate_temperature(data_path)
    generate_wind(data_path, seed)
    generate_moisture(data_path)
    generate_biomes(data_path)
    render_image(data_path)

def generate_coastline(data_path, water_level, show_france, seed):
    if os.path.isfile(data_path + "coastline.pkl"):
        # Already did this.
        return
    data = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH))
    for i in range(IMAGE_HEIGHT):
        for j in range(IMAGE_WIDTH):
            data[i,j] = get_elevation(
                MAP_WIDTH*(float(j)/IMAGE_WIDTH),
                MAP_HEIGHT*(float(i)/IMAGE_HEIGHT),
                seed)
    
    pickle.dump(data, open(data_path+"rough_elevation.pkl", 'wb'))
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
    pickle.dump(data, open(data_path+"coastline.pkl", 'wb'))

def generate_elevation(data_path, seed):
    if os.path.isfile(data_path + "elevation.pkl"):
        return
    coastline = pickle.load(open(data_path+"coastline.pkl", 'rb'))
    elevation = pickle.load(open(data_path+"rough_elevation.pkl", 'rb'))

    for i in range(IMAGE_HEIGHT):
        for j in range(IMAGE_WIDTH):
            elevation[i,j] += get_elevation(
                    MAP_WIDTH*DETAIL_SCALE*(float(j)/IMAGE_WIDTH),
                    MAP_HEIGHT*DETAIL_SCALE*(float(i)/IMAGE_HEIGHT),
                    seed)
    elevation = np.exp(REDIST_STRENGTH*elevation)
    elevation = coastline * elevation
    plt.imshow(elevation)
    plt.show()
    pickle.dump(elevation, open(data_path+"elevation.pkl", 'wb'))

def generate_temperature(data_path):
    if os.path.isfile(data_path + "temperature.pkl"):
        return
    
    elevation = pickle.load(open(data_path+"elevation.pkl", 'rb'))
    scaled_elevation = imresize(elevation, (NGRID_Y, NGRID_X))
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
    pickle.dump(temp, open(data_path+"temperature.pkl", 'wb'))

def generate_wind(data_path, seed):
    if os.path.isfile(data_path + "wind.pkl"):
        return

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
    pickle.dump(wind, open(data_path+"wind.pkl", 'wb'))

def generate_moisture(data_path):
    if os.path.isfile(data_path + "moisture.pkl"):
        return

    elevation = pickle.load(open(data_path+"elevation.pkl", 'rb'))
    scaled_elevation = imresize(elevation, (NGRID_Y, NGRID_X))
    wind = pickle.load(open(data_path+"wind.pkl", 'rb'))
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
    pickle.dump(moisture, open(data_path+"moisture.pkl", 'wb'))

def generate_biomes(data_path):
    if os.path.isfile(data_path + "biomes.pkl"):
        return
    
    moisture = pickle.load(open(data_path+"moisture.pkl", 'rb'))
    moisture = imresize(moisture, (IMAGE_HEIGHT, IMAGE_WIDTH))
    plt.imshow(moisture)
    plt.show()
    moisture = np.digitize(moisture, [0, 100, 170, 230, 255])-1
    moisture[moisture > 4] = 4
    plt.imshow(moisture)
    plt.show()
    temp = pickle.load(open(data_path+"temperature.pkl", 'rb'))
    temp = imresize(temp, (IMAGE_HEIGHT, IMAGE_WIDTH))
    plt.imshow(temp)
    plt.show()
    temp = np.digitize(temp, [0, 90, 130, 255])-1
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
    elevation = pickle.load(open(data_path+"elevation.pkl", 'rb'))
    img[elevation == 0] = OCEAN
    plt.imshow(img)
    plt.show()
    pickle.dump(img, open(data_path+"biomes.pkl", 'wb'))

def render_image(data_path):
    elevation = pickle.load(open(data_path+"elevation.pkl", 'rb'))
    biomes = pickle.load(open(data_path+"biomes.pkl", 'rb'))

    final_image = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), dtype=np.uint8)
    for i in range(IMAGE_HEIGHT):
        for j in range(IMAGE_WIDTH):
            final_image[i,j,:] = biome_colours[biomes[i,j]]

    noise1 = np.random.randint(20, size=(IMAGE_HEIGHT, IMAGE_WIDTH, 1))
    noise2 = np.random.randint(20, size=(IMAGE_HEIGHT, IMAGE_WIDTH, 1))
    noise1 = np.tile(noise1, (1,1,3))
    noise2 = np.tile(noise2, (1,1,3))
    noise1[final_image > 255-noise1] = 0
    noise2[final_image < noise2] = 0
    final_image += noise1.astype(np.uint8)
    final_image -= noise2.astype(np.uint8)
    
    # Light the image
    light_vector = [3, 3]
    shadows = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3))
    for i in range(IMAGE_HEIGHT):
        for j in range(IMAGE_WIDTH):
            if i > light_vector[0] and i < IMAGE_HEIGHT+light_vector[0] and \
                j > light_vector[1] and j < IMAGE_WIDTH+light_vector[1]:
                if elevation[i-light_vector[0], j-light_vector[0]] > \
                    elevation[i,j] and elevation[i,j] > 0:
                    shadows[i,j,:] = 1
    final_image[shadows == 1] /= SHADOW_STRENGTH
    plt.imshow(final_image)
    plt.show()
   
def rescale(array):
    array -= (np.amin(array))
    array /= np.amax(array)
    array = 2*array - 1
    return array
    
def get_elevation(x, y, seed=0):
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
