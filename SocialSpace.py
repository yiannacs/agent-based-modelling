# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 18:12:40 2022

"""
import random
from SocialAgents import Agent, Activist
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

class SocialSpace:
    def __init__(self, shape):
        self.nodes = {}
        self.edges = {}
        self.shape = shape
        
    def nodes(self):
        return self.nodes
    
    def edges(self):
        return self.edges

    def capacity(self):
        return self.shape[0] * self.shape[1]
    
    def update_node(self, node_loc, node):
        if isinstance(node_loc, tuple):
            node_index = node_loc[0] * self.shape[1] + node_loc[1]
        else:
            node_index = node_loc

        if node_index >= self.capacity():
            print('Node {} is out of bounds of grid of shape {}, capacity {}'.format(node_index,
                                                                                     self.shape,
                                                                                     self.capacity()))
            return

        self.nodes[node_index] = node

    def tally(self, print_to_jpeg=False, img_name=None):
        red_private = 0
        red_inner_circle = 0
        red_public = 0
        
        blue_private = 0
        blue_inner_circle = 0
        blue_public = 0
        
        BLUE_PRIVATE = 0
        BLUE_INNER_CIRCLE = 1
        BLUE_PUBLIC = 2
        RED_PRIVATE = 3
        RED_INNER_CIRCLE = 4
        RED_PUBLIC = 5
            
        # Generate grid for printing
        nrows = self.shape[0]
        ncols = self.shape[1]
        image = np.zeros(nrows*ncols)

        node_i = 0
        for node in self.nodes.values():
            if node.attitude == 'red':
                if node.expression_level == 'private':
                    red_private += 1
                    image[node_i] = RED_PRIVATE
                elif node.expression_level == 'inner_circle':
                    red_inner_circle += 1
                    image[node_i] = RED_INNER_CIRCLE
                elif node.expression_level == 'public':
                    red_public += 1
                    image[node_i] = RED_PUBLIC
            elif node.attitude == 'blue':
                if node.expression_level == 'private':
                    blue_private += 1
                    image[node_i] = BLUE_PRIVATE
                elif node.expression_level == 'inner_circle':
                    blue_inner_circle += 1
                    image[node_i] = BLUE_INNER_CIRCLE
                elif node.expression_level == 'public':
                    blue_public += 1
                    image[node_i] = BLUE_PUBLIC
            node_i += 1
            
        if print_to_jpeg:
            image = image.reshape((nrows, ncols))

            row_labels = range(nrows)
            col_labels = range(ncols)
            
            cmap = mpl.colors.ListedColormap(['paleturquoise', 'skyblue', 'navy',
                                              'lightcoral', 'red', 'firebrick'])
            
            plt.matshow(image, cmap=cmap)
            index = img_name.split('_')[-1]
            plt.title(index[:-4] + "th Generation")

            plt.axis('off')
            plt.savefig(img_name)
            plt.clf()
            plt.close('all')
                  
        return blue_private, blue_inner_circle, blue_public, red_private, red_inner_circle, red_public
            
    # From Muthukrishna, adapted for SocialSpace class 
    def mingle(self, iterations):
        space = deepcopy(self)

        # Store initial location of all people
        locations = {}
        for key_j in space.nodes.keys():
            # Resistant to empty cells in the grid
            locations[key_j] = (int(key_j/space.shape[1]), key_j % space.shape[1])

        for i in range(iterations):
            matches = {}
            # Stochastically move every person in the grid, make them friends if they meet at a location
            for key_j in space.nodes.keys():
                # Move people (and possibly make friends) with probability given by their extroversion
                if random.random() < space.nodes[key_j].extroversion:
                    new_location_j = SocialSpace.migrate(locations[key_j], space.shape)

                    # Check if there's people in the new (might be the same) location
                    if new_location_j in matches:
                        for key_k in matches[new_location_j]:
                            # Add every key_k in matches[new_location_j] to key_j's edges
                            if key_j in space.edges:
                                space.edges[key_j].add(key_k)
                            else:
                                space.edges[key_j] = {key_k}

                            # Add key_j to the edged of every key_k in matches[new_location_j]
                            if key_k in space.edges:
                                space.edges[key_k].add(key_j)
                            else:
                                space.edges[key_k] = {key_j}
                    else:
                        matches[new_location_j] = [key_j]

                    locations[key_j] = new_location_j
        
        return space

    # From Muthukrishna, adapted for SocialSpace class, always wraps
    def migrate(location, grid):
        # Travel along vertical/horizontal axis with uniform probability distribution
        location = (location[0] + random.choice([-1,0,1]),location[1] + random.choice([-1,0,1]))

        location0 = location[0]
        location1 = location[1]

        # Wrap around rows
        if location[0] < 0:
            location0 = grid[0] - 1
        elif location[0] >= grid[0]:
            location0 = 0
        
        # Wrap around columns
        if location[1] < 0:
            location1 = grid[1] - 1
        elif location[1] >= grid[1]:
            location1 = 0
        
        location = (location0, location1)
        return location
    