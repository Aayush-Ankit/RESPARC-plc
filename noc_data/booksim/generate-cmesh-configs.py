# Python script to generate different noc config files for booksim simulations
import os
import sys
root_path = os.path.dirname(os.path.abspath(__file__))

nc_size_list = [x for x in range (2, 22,2)]
router_list = ['cmesh']

# simulation parameters
cmesh_conc = 4
noc_num_dim = 2
sample_period = 1000 # number of simulator cycles to be treated as one sample (throws stats at each sample period)
warmup_periods = 3
sim_type = 'latency'
traffic = 'uniform'
packet_size = 128 # bits
cmesh_flit_size = 16 # bits
mesh_flit_size = 8 # bits
injection_rate = 0.01 # typically, neuron fan-in >> xbar size -> So, inj_rate of 0.01 an dnot 0.04
latency_thres = 10000.0

''' Sample Config File from booksim/examples
//cmesh_concentrated mesh configuration file running batch mode
//xr, yr, x, y, are use to indicate how the cmesh_concnetration is formed.
topology = cmesh;
k = 4;
n = 2;
c = 4;
xr = 2;
yr = 2;
x = 4;
y = 4;
routing_function = dor_no_express;
traffic = bitcomp;
use_read_write = 0;
batch_size = 2000;
'''

def generate_cmesh_topology (nc_size, cmesh_conc):
    text = "routing_function = dor_no_express;\n\
topology = cmesh;\n\
k = " + str(nc_size/(cmesh_conc/2)) + ";\n\
n = " + str(noc_num_dim) + ";\n\
c = " + str(cmesh_conc) + ";\n\
x = " + str(nc_size/(cmesh_conc/2)) + ";\n\
y = " + str(nc_size/(cmesh_conc/2)) + ";\n\
xr = " + str(2) + ";\n\
yr = " + str(2) + ";\n\
packet_size = " + str(packet_size/cmesh_flit_size) + ";\n"
    return text

def generate_mesh_topology (nc_size):
    text = "routing_function = dor_no_express;\n\
topology = mesh;\n\
k = " + str(nc_size) + ";\n\
n = " + str(noc_num_dim) + ";\n\
packet_size = " + str(packet_size/mesh_flit_size) + ";\n"
    return text

end_common_text = "traffic = " + traffic + ";\n\
sim_type = " + sim_type + ";\n\
sample_period = " + str(sample_period) + ";\n\
warmup_periods = " + str(warmup_periods) + ";\n\
injection_rate = " + str(injection_rate) + ";\n\
latency_thres = " + str(latency_thres) + ";\n"
# Note: Default injection rate is in packets/flit cycles.


# Create a config files for all nc_size and router configuration
for router in router_list:
    for nc_size in nc_size_list:
        filename = root_path + '/configs/' + router + '-' + str(nc_size)
        fid = open(filename, 'w')
        if (router == 'cmesh'):
            fid.write(generate_cmesh_topology(nc_size, cmesh_conc))
        elif (router == 'mesh'):
            fid.write(generate_mesh_topology(nc_size))
        else:
            sys.exit ('router type not supported')
        fid.write(end_common_text)
        fid.close()


