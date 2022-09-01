import random
import numpy as np
import argparse
from SocialAgents import *
from SocialSpace import *
from copy import copy
import csv
import os

###################################################
# Settings params
###################################################
GENERATE_IMAGES = False
N_SIMULATIONS = 1
DATA_FOLDER = './data/'
IMG_FOLDER = './img/'
IMG_FREQ = 1000

###################################################
# Environment
###################################################
SIZE_OF_SPACE = (30,30)

label_scenario = 0
P_MINORITY = 0.1
dist_extroversion = 'baseline'
dist_influenceability = 'baseline'

###################################################
# Strategy
###################################################
label_strategy = 'baseline_gif'

NUMBER_OF_GROUPS = 10
act_consistency = 0.5
dist_influence_power = 'baseline'
dist_rigidness = 'baseline'

# Shouldn't change ANYTHING from this point on
GROUPS_UPPER_LIMITS = [i*1.0/NUMBER_OF_GROUPS for i in range(1, NUMBER_OF_GROUPS + 1)]

###################################################
# Constants
###################################################
SOCIAL_NETW_ITERATIONS = 50

INFLUENCIABILITY_PARAMS = {
    'baseline' : [4.0, 4.0],
    'resistant' : [2.5, 3.5],
    'susceptible' : [3.5, 2.5]}

EXTROVERSION_PARAMS = {
    'baseline' : [4.0, 4.0],
    'introverted' : [2.5, 3.5],
    'extroverted' : [3.5, 2.5]}

INFLUENCE_POWER_PARAMS = {
    'baseline' : [4.0, 4.0],
    'noninfluential' : [1.5, 3.5],
    'influential' : [3.5, 1.5]}

RIGIDNESS_PARAMS = {
    'baseline' : [4.0, 4.0],
    'rigid' : [1.5, 3.5],
    'flexible' : [3.5, 1.5]}

# blue: Majority ; red: Minority
ATTITUDES = ['blue', 'red']  
ATTITUDE_BLUE = 0
ATTITUDE_RED = 1

EXPRESSION_LEVELS = ['private', 'inner_circle', 'public']
EXP_LVL_PRIVATE = 0
EXP_LVL_INNER_CIRCLE = 1
EXP_LVL_PUBLIC = 2

RIGIDNESS = []

###################################################
# Helper Functions
###################################################

def choose_group(groups, n_activists):
    p = []
    
    for group_i in groups:
        p.append(float(group_i.size)/n_activists)
        
    return np.random.choice(range(0, len(groups)), p=p)

def count_influencing_friends(space, node):
    n_friends_red = 0
    n_friends = 0
    
    if node in space.edges:
        friends = space.edges[node]
        n_friends = len(friends)

        n_friends_red = 0
        for friend in friends:
            if space.nodes[friend].attitude == 'red' and \
                (space.nodes[friend].expression_level == 'inner_circle' or space.nodes[friend].expression_level == 'public'):
                    n_friends_red += 1
                
    return n_friends_red, n_friends
        
###################################################
# Main
###################################################
# Make sure folders exist
if not os.path.exists(DATA_FOLDER):
  # Create a new directory because it does not exist 
  os.makedirs(DATA_FOLDER)
  
if GENERATE_IMAGES == True:  
    if not os.path.exists(IMG_FOLDER):
        # Create a new directory because it does not exist 
        os.makedirs(IMG_FOLDER)

    for i in range(0, N_SIMULATIONS):
        tmp_path = IMG_FOLDER + '{}/'.format(i)
        
        if not os.path.exists(tmp_path):
            # Create a new directory because it does not exist 
            os.makedirs(tmp_path)
  
# Create a 5x5 2D grid:
social_space = SocialSpace(SIZE_OF_SPACE)

# Initialise nodes in social space
activist_groups = [ActivistGroup() for i in range(NUMBER_OF_GROUPS)]
for i in range(social_space.capacity()):
    extroversion = np.random.beta(*EXTROVERSION_PARAMS[dist_extroversion])
    influenceability = np.random.beta(*INFLUENCIABILITY_PARAMS[dist_influenceability])
    attitude = ATTITUDE_RED if np.random.random() < P_MINORITY else ATTITUDE_BLUE
    if np.random.random() >= extroversion:
        expression_level = EXP_LVL_PRIVATE
    else:
        if np.random.random() >= extroversion:
            expression_level = EXP_LVL_INNER_CIRCLE
        else:
            expression_level = EXP_LVL_PUBLIC

    new_agent = Agent(extroversion, influenceability, ATTITUDES[attitude], EXPRESSION_LEVELS[expression_level])
    
    # Possibly make them an activist
    if ATTITUDES[attitude] == 'red' and EXPRESSION_LEVELS[expression_level] == 'public':
        if np.random.random() < extroversion:
            # Make them an activist
            influence_power = np.random.beta(*INFLUENCE_POWER_PARAMS[dist_influence_power])
            rigidness = np.random.beta(*RIGIDNESS_PARAMS[dist_rigidness])
            new_agent = Activist.from_Agent(new_agent, influence_power, rigidness)
            # print('Activist creater. count = {}'.format(Activist.activist_count))
            
            # Determine to what group the new activist belongs
            for group in range(len(GROUPS_UPPER_LIMITS)):
                if rigidness <= GROUPS_UPPER_LIMITS[group]:
                    i_group = group
                    break
            
            # Update group
            activist_groups[i_group].update(influence_power, rigidness)

    social_space.update_node(i, new_agent)

# Generate social networks
social_space = social_space.mingle(SOCIAL_NETW_ITERATIONS)

# Set activist consistency 
ActivistGroup.set_consistency(act_consistency)

# Run interactions
fields = ['simulation', 
          'generation', 
          'p_j',
          'p_act',
          'n_activists',
          'blue_total', 
          'blue_private', 
          'blue_inner_circle', 
          'blue_public', 
          'red_total', 
          'red_private', 
          'red_inner_circle', 
          'red_public']
file_name = DATA_FOLDER + 'results_' + \
    'scenario-' + str(label_scenario) + \
    '_strategy-' + str(label_strategy) + \
    '.csv'
    
file = open(file_name, 'w', newline='')
writer = csv.DictWriter(file, fieldnames=fields, delimiter=',')
writer.writeheader()

activist_count_initial = Activist.activist_count
for simulation_i in range(0, N_SIMULATIONS):
    Activist.reset_count(activist_count_initial)
    activist_groups_i = deepcopy(activist_groups)
    
    print('\nSimulation {}'.format(simulation_i))
    social_space_i = deepcopy(social_space)
    count_no_change = 0
    n_agents = len(social_space_i.nodes.keys())

    img_name = IMG_FOLDER + '{}/'.format(simulation_i) + 'results_' + \
        'scenario-' + str(label_scenario) + \
        'strategy-' + str(label_strategy)
    
    # Save initial state to file
    generation_i = 0
    img_name_i = img_name + '_' + str(generation_i) + '.png'
    blue_private, blue_inner_circle, blue_public, \
        red_private, red_inner_circle, red_public = social_space_i.tally(print_to_jpeg=GENERATE_IMAGES,
                                                                       img_name=img_name_i)
    
    data = {}
    data['simulation'] = simulation_i
    data['generation'] = generation_i
    data['p_j'] = 0
    data['p_act'] = 0
    data['n_activists'] = Activist.activist_count
    data['blue_total'] = blue_private + blue_inner_circle + blue_public
    data['blue_private'] = blue_private
    data['blue_inner_circle'] = blue_inner_circle
    data['blue_public'] = blue_public
    data['red_total'] = red_private + red_inner_circle + red_public
    data['red_private'] = red_private
    data['red_inner_circle'] = red_inner_circle
    data['red_public'] = red_public
    
    writer.writerow(data)
    
    p_act = 0
    while count_no_change < 2*n_agents:
        generation_i += 1
        node_i = list(social_space_i.nodes.keys())[np.random.randint(0, n_agents)]
        n_friends_red, n_friends = count_influencing_friends(social_space_i, node_i)
        
        # Determine if node_i is approached by activists:
        n_activists = 0
        p_act = 0
        p_friends = 0
        rigidness_avg = 1
        if np.random.random() < Activist.activist_count/n_agents:
            # Determine by which group
            group = choose_group(activist_groups_i, Activist.activist_count)
            n_activists = activist_groups_i[group].size
            
            # Compute effect of the group
            rigidness_avg = activist_groups_i[group].sum_rigidness / n_activists
            influence_avg = activist_groups_i[group].sum_influence / n_activists
            
            p_act = n_activists * rigidness_avg * influence_avg * ActivistGroup.consistency / (n_activists + n_friends)
        
        # Probability of influence due to acquaintances
        if n_friends + n_activists != 0:
            p_friends = n_friends_red / (n_friends + n_activists)
        
        # Composite probability of influence
        p_influence = (p_friends + p_act) * social_space_i.nodes[node_i].influenceability
        
        prev_attitude = copy(social_space_i.nodes[node_i].attitude)
        prev_expression = copy(social_space_i.nodes[node_i].expression_level)
        if np.random.random() < p_influence:
            # Person changes their mind
            social_space_i.nodes[node_i].update_attitude(rigidness_avg)

            # Possibly make them an activist
            if social_space_i.nodes[node_i].attitude == 'red' and \
                social_space_i.nodes[node_i].expression_level == 'public' and \
                not isinstance(social_space_i.nodes[node_i], Activist):
                if np.random.random() < social_space_i.nodes[node_i].extroversion:
                    # Make them an activist
                    influence_power = np.random.beta(*INFLUENCE_POWER_PARAMS[dist_influence_power])
                    rigidness = np.random.beta(*RIGIDNESS_PARAMS[dist_rigidness])
                    new_agent = Activist.from_Agent(new_agent, influence_power, rigidness)
                    # print('Activist created. count = {}'.format(Activist.activist_count))
                    
                    # Determine to what group the new activist belongs
                    for group in range(len(GROUPS_UPPER_LIMITS)):
                        if rigidness <= GROUPS_UPPER_LIMITS[group]:
                            i_group = group
                            break
                    
                    # Update group
                    activist_groups_i[i_group].update(influence_power, rigidness)
                    social_space_i.update_node(node_i, new_agent)

        if prev_attitude == social_space_i.nodes[node_i].attitude and \
            prev_expression == social_space_i.nodes[node_i].expression_level:
                count_no_change += 1
        else:
            count_no_change = 0
    
        img_name_i = img_name + '_' + str(generation_i) + '.png'
        if generation_i % IMG_FREQ == 0:
            blue_private, blue_inner_circle, blue_public, \
                red_private, red_inner_circle, red_public = social_space_i.tally(print_to_jpeg=GENERATE_IMAGES,
                                                                           img_name=img_name_i)
        else:
            blue_private, blue_inner_circle, blue_public, \
                red_private, red_inner_circle, red_public = social_space_i.tally()
            
        data['simulation'] = simulation_i
        data['generation'] = generation_i
        data['p_j'] = p_influence
        data['p_act'] = p_act * social_space_i.nodes[node_i].influenceability
        data['n_activists'] = Activist.activist_count
        data['blue_total'] = blue_private + blue_inner_circle + blue_public
        data['blue_private'] = blue_private
        data['blue_inner_circle'] = blue_inner_circle
        data['blue_public'] = blue_public
        data['red_total'] = red_private + red_inner_circle + red_public
        data['red_private'] = red_private
        data['red_inner_circle'] = red_inner_circle
        data['red_public'] = red_public
        
        writer.writerow(data)
    
    if GENERATE_IMAGES:
        blue_private, blue_inner_circle, blue_public, \
            red_private, red_inner_circle, red_public = social_space_i.tally(print_to_jpeg=GENERATE_IMAGES,
                                                                        img_name=img_name_i)
    
file.close()
            
print('DONE')
