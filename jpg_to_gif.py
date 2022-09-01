from fileinput import filename
import imageio
from os import listdir
from os.path import isfile, join
import os
mypath = './img/0/'
filenames = os.listdir(mypath)
filenames.sort(key = lambda x:int(x.split('_')[-1][:-4]))

images = []
for filename in filenames:
    images.append(imageio.imread(mypath + filename))
imageio.mimsave(mypath + 'result.gif', images)