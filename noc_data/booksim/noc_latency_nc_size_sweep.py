# script to simulate NOC config files on booksim and aggregate results
import os
import sys
import collections
import matplotlib.pylab as plt

# specify simulation paths
root_path = os.path.dirname(os.path.abspath(__file__))
trace_path = os.path.join(root_path, "traces")
resparcPLC_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
simulator_path = os.path.join(resparcPLC_path, "booksim2/src")


# check if config files exist
config_path = root_path + '/configs/'
assert (os.path.isdir(config_path) and (os.listdir(config_path) != [])), "No config file found"

## run booksim2 on all config files and store traces
#trace_path = root_path + '/traces/'
#for file_name in os.listdir(config_path):
#    config_file_path = config_path + file_name
#    trace_file_path = trace_path + file_name
#    run_command = simulator_path + "/booksim " + config_file_path + " > " + trace_file_path
#    print ('Runnning ' + file_name + '.....\n')
#    os.system (run_command)

# extract average, minimum and maximum latency, hop_average
num_file = len(os.listdir(trace_path))
# create dictionary to store recorder values
minimum_latency = {}
maximum_latency = {}
average_latency = {}
average_hop = {}

for file_name in os.listdir(trace_path):
    f = open(os.path.join(trace_path,file_name), 'r')
    found_overall_stats = 0
    for line in f:
        if ('Overall Traffic Statistics') in line:
            found_overall_stats = 1
        elif ('Network latency average') in line:
            found_overall_stats = 0

        # extract average, miminum and maximum packet latency
        config_idx = int(file_name.split('-')[1])
        if (found_overall_stats):
            if ('average' in line):
                temp_val = float((line.split('(')[0]).split('=')[1])
                average_latency[config_idx] = temp_val
            elif ('minimum' in line):
                temp_val = float((line.split('(')[0]).split('=')[1])
                minimum_latency[config_idx] = temp_val
            elif ('maximum' in line):
                temp_val = float((line.split('(')[0]).split('=')[1])
                maximum_latency[config_idx] = temp_val

        # extract average hops
        if ('Hops average' in line):
            temp_val = float((line.split('(')[0]).split('=')[1])
            average_hop[config_idx] = temp_val

#print (minimum_latency)
#print (maximum_latency)
#print (average_latency)
#print (average_hop)

# plot the latency values vs nc_size
x, avg_lat = zip(*(sorted(average_latency.items())))
x, max_lat = zip(*(sorted(maximum_latency.items())))
x, min_lat = zip(*(sorted(minimum_latency.items())))
x, avg_hop = zip(*(sorted(average_hop.items())))

f, arr = plt.subplots(2,2)
arr[0,0].plot(x, avg_lat, 'o-', 'r')
arr[0,0].set_title('Average packet latency')
arr[0,0].set_ylabel('Latency (cycles)')
#arr[0,0].set_xlabel('Neurocell size')

arr[0,1].plot(x, max_lat, '.-')
arr[0,1].set_title('Maximum packet latency')
arr[0,1].set_ylabel('Latency (cycles)')
#arr[0,1].set_xlabel('Neurocell size')

arr[1,0].plot(x, min_lat, 'v-')
arr[1,0].set_title('Minimum packet latency')
arr[1,0].set_ylabel('Latency (cycles)')
#arr[1,0].set_xlabel('Neurocell size')

arr[1,1].plot(x, avg_hop, 'x-')
arr[1,1].set_title('Average energy per packet transfer')
arr[1,1].set_ylabel('Number of Hops')
#arr[1,1].set_xlabel('Neurocell size')

plt.show()




