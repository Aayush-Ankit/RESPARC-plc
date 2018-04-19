import itertools

## Code to generate prototxt files
num_classes = 10

#Junk
num_conv = [0] #number of convolution layers
ker_size = 5
feature_size_list = [10, 25, 50]

#Useful parameters - only specify neurons in non-input layers
num_fcl = [[128, 10],
           [256, 10],
           [512, 10],
           [512, 512, 10],
           [1024, 512, 10],
           [1024, 512, 128, 10]]

index = 0
filename = 'train_cifar_trials.sh'

start_text = '#!/usr/bin/env sh \n\
set -e\n'

solver_path = 'EnhancedRESPARC_Powerline/cifar10/solver/'
trace_path = 'EnhancedRESPARC_Powerline/cifar10/traces/'

fid = open(filename, 'w')
fid.write(start_text)
for num_conv_layers in num_conv:
    num_feature = [p for p in itertools.product(feature_size_list, repeat=num_conv_layers)] #generates all permutations with repeatitions
    for feature_tuple in num_feature:
        for net in num_fcl:
            text = './build/tools/caffe train --solver=' + solver_path + 'cifar_solver_' + str(index) + \
                '.prototxt $@ 2>&1 | tee ' + trace_path + 'solver_' + str(index) + '_trace.txt\n'
            index = index + 1
            fid.write(text)

fid.close()
print (index)



