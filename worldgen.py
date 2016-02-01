from collections import deque
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d

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
        self.vertex_elevations = []
        self.water = False
        self.biome = BARE
        self.neighbours = []
        self.visited = False

def generate(num_points,
             num_mountains,
             mountain_determination=0.8,
             mountain_dropoff=0.9,
             elevation_noise=0.1,
             landgen_iterations=10,
             water_level=0):
    points = np.random.uniform(size=(num_points,2))
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
    for i in range(num_mountains):
        start_index = np.random.randint(len(regions))
        direction = np.random.uniform(low=-1., high=1., size=2)
        regions[start_index].elevation = 1
        for r in regions[start_index].neighbours:
            r.elevation = 1
        queue = deque([regions[start_index]])
        while len(queue) > 0:
            region = queue.pop()
            generate_mountains(region, direction, mountain_determination,
                mountain_dropoff, elevation_noise)
            queue.extend([n for n in region.neighbours if not n.visited])
            region.visited = True
        for region in regions:
            region.visited = False
            if region.elevation > 1:
                region.elevation = 1
            region.elevation += water_level
            if region.elevation < 0:
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
    plt.show()
