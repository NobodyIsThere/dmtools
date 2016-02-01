from collections import deque
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from noise import snoise2
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d

MAP_WIDTH = 2.
MAP_HEIGHT = 1.

CONTINENT_SCALE = 2
DETAIL = 0.5

OCEAN = 0
BARE = 1

colors = \
{
    OCEAN: '#0000ff',
    BARE: '#cccccc'
}

class Region(object):
    def __init__(self, coords, vertices):
        self.coords = coords
        self.vertices = vertices
        self.elevation = 0
        self.vertex_elevations = [0]*len(vertices)
        self.water = False
        self.biome = BARE
        self.neighbours = []
        self.visited = False

def generate(num_points,
             perlin_octaves=10,
             perlin_persistence=0.8,
             perlin_lacunarity=2.0,
             water_level=0,
             seed=0):
    xpoints = np.random.uniform(high=MAP_WIDTH, size=num_points)
    ypoints = np.random.uniform(high=MAP_HEIGHT, size=num_points)
    points = zip(xpoints, ypoints)
    vor = Voronoi(points)
    
    region_dict = {}
    regions = []
    for i, point in enumerate(vor.points):
        vert_inds = vor.regions[vor.point_region[i]]
        if -1 in vert_inds:
            continue
        vertices = [vor.vertices[j] for j in vert_inds]
        region = Region(point, vertices)
        for vert_ind in vert_inds:
            if vert_ind in region_dict:
                for other_region in region_dict[vert_ind]:
                    if other_region not in region.neighbours:
                        region.neighbours.append(other_region)
                    if region not in other_region.neighbours:
                        other_region.neighbours.append(region)
            else:
                region_dict[vert_ind] = []
            region_dict[vert_ind].append(region)
        regions.append(region)
    
    # Now do elevation
    for region in regions:
        for i, vertex in enumerate(region.vertices):
            # Large-scale features
            region.vertex_elevations[i] = \
                snoise2(CONTINENT_SCALE*vertex[0],
                    CONTINENT_SCALE*vertex[1],
                    octaves=1, base=2*seed, repeatx=MAP_WIDTH*CONTINENT_SCALE)
            region.vertex_elevations[i] += \
                DETAIL*snoise2(vertex[0], vertex[1],
                    octaves=perlin_octaves, persistence=perlin_persistence,
                    lacunarity=perlin_lacunarity,
                    base=seed, repeatx=MAP_WIDTH)
        region.elevation = np.mean(region.vertex_elevations)
    
    for region in regions:
        if region.elevation > 1:
            region.elevation = 1
        if region.elevation < water_level:
            region.biome = OCEAN
    
    draw(regions)

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
