import random
import numpy as np

class Agent:
    red_count = 0
    blue_count = 0

    def __init__(self, extroversion, influenceability, attitude, expression_level):
        self.extroversion = extroversion            # extroversion = Propension to make acquaintances
        self.influenceability = influenceability    # influenceability = Propension to be influenced
        self.attitude = attitude                    # attitude = [blue, red]
        self.expression_level = expression_level    # expression_level = [Private, InnerCircle, Public]

        if self.attitude == 'red':
            Agent.red_count += 1
        if self.attitude == 'blue':
            Agent.blue_count += 1
            
    def update_attitude(self, rigidness):
        deep = not (np.random.random() < rigidness)
        # This assumes only red activists
        if self.attitude == 'blue':
            if self.expression_level == 'public':
                if deep:
                    self.attitude = 'red'
                    self.expression_level = 'private'
                else:
                    self.attitude = 'blue'
                    self.expression_level = 'inner_circle'
            elif self.expression_level == 'inner_circle':
                if deep:
                    self.attitude = 'red'
                    self.expression_level = 'private'
                else:
                    self.attitude = 'blue'
                    self.expression_level = 'private'
            elif self.expression_level == 'private':
                if deep:
                    self.attitude = 'red'
                    self.expression_level = 'public'
                else:
                    self.attitude = 'red'
                    self.expression_level = 'public'
        else: # red
            if self.expression_level == 'public':
                self.attitude = 'red'
                self.expression_level = 'public'
            elif self.expression_level == 'inner_circle':
                self.attitude = 'red'
                self.expression_level = 'public'
            elif self.expression_level == 'private':
                self.attitude = 'red'
                self.expression_level = 'inner_circle'       

class ActivistGroup:
    consistency = 0
    
    def __init__(self):
        self.size = 0
        self.sum_influence = 0
        self.sum_rigidness = 0
    
    def update(self, influence_power, rigidness):
        self.size = self.size + 1
        self.sum_influence = self.sum_influence + influence_power
        self.sum_rigidness = self.sum_rigidness + rigidness
        
    @classmethod
    def set_consistency(cls, consistency):
        cls.consistency = consistency

class Activist(Agent):
    activist_count = 0
    
    # Agent.__init__(self, extroversion, influenceability, attitude, expression_level)
    # Setting all attributes as optional to make it easier to generate Activist from Agent,
    # which is the way Activists are *always* created 
    def __init__(self,
                 extroversion=0.5, 
                 influenceability=0.5, 
                 attitude='red', 
                 expression_level='public', 
                 influence_power=0.5,
                 rigidness=0.5):  
        # Set instance attributes
        super().__init__(extroversion, influenceability, attitude, expression_level)
        self.influence_power = influence_power

        # Update count
        Activist.activist_count += 1

    # https://stackoverflow.com/a/65371711
    @classmethod
    def from_Agent(cls, ag: Agent, influence_power, rigidness):
        # Create new activist
        act = cls(influence_power=influence_power,
                  rigidness=rigidness)

        # Copy all values of original Agent ag to Activist act
        for key, value in ag.__dict__.items():
            act.__dict__[key] = value
        return act
    
    @classmethod
    def reset_count(cls, initial_count=0):
        cls.activist_count = initial_count