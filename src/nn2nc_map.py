# Map the Neural Network (synapses_neurons) onto a NeuroCell
import math
import numpy as np

xbar_per_mpe = 4
xbar_size = 64

# find the NC size for an NN
def get_NCsize (net, inp_size):
    num_xbar = 0
    num_in = float(inp_size**2)
    for fcn in net:
        num_out = float(fcn)
        num_xbar = num_xbar + (math.ceil((num_in / xbar_size)) * math.ceil((num_out / xbar_size)))
        num_in = num_out # set input for next layer
    num_mpe = math.ceil(num_xbar / xbar_per_mpe)
    nc_size  = math.ceil(math.sqrt(num_mpe))
    return int(nc_size)

# initialzie an NC of given size based on an NN
def init_NC (nc_size):
    NC = np.zeros((nc_size, nc_size, xbar_per_mpe),
                  dtype=[('neuron_gid', 'int8'), ('layer_id', 'int8')])
    last_mapped_mpe = {'x':0, 'y':-1}
    return NC, last_mapped_mpe

# assigns synapses and output neurons to the NC
# Assumption - an mpe maps neurons/synapses from one layer only
def assign_layer2NC (NC, num_in, num_out, layer_id, last_mapped_mpe):
    # last mapped mpe
    curr_mpeX = last_mapped_mpe['x'] if (last_mapped_mpe['y'] != len(NC)) else last_mapped_mpe['x'] + 1
    curr_mpeY = (last_mapped_mpe['y'] + 1) % len(NC)

    # start the NC mapping of a neurons in layers - each PE - dict(neuron_gid, layer_id)
    # both neuron_gid (layer_id) of 0 means unmapped neurons (synapses)
    neuron_gid = 1 # gid -> group_id
    num_in_temp = num_in
    num_out_temp = num_out
    break_status = 0 # tracks when all neurons in layer have been mapped
    for i in range(curr_mpeX, len(NC)):
        for j in range(0, len(NC)):
            if (NC[j,i,0]['layer_id'] != 0): # Skip the mpes in the current column which have already been mapped
                continue
            for k in xrange(xbar_per_mpe):
                # Start a new assignment of output neurons
                if ((num_in_temp == num_in) and (num_out_temp > 0)):
                    # Assign neurons
                    NC[j,i,k]['neuron_gid'] = neuron_gid
                    neuron_gid = neuron_gid + 1
                    num_out_temp = num_out_temp - xbar_size
                    # Assign layer
                    NC[j,i,k]['layer_id'] = layer_id
                    num_in_temp = num_in_temp - xbar_size
                elif ((num_in_temp > 0)):
                    # Assign layer
                    NC[j,i,k]['layer_id'] = layer_id
                    num_in_temp = num_in_temp - xbar_size
                    if ((num_in_temp <= 0) and (num_out_temp > 0)):
                        num_in_temp = num_in
                    elif ((num_in_temp <= 0) and (num_out_temp <= 0)):
                        break_status = 1
                        # record the last mapped mpe
                        last_mapped_mpe['x'] = i
                        last_mapped_mpe['y'] = j
                        break
            if (break_status == 1):
                break
        if (break_status == 1):
            break

    return NC, last_mapped_mpe

# Analyze the conenctivity of a mapped NN onto NC
def analyze_connectivity (nn2nc_map):
    net = nn2nc_map['nn']
    map_t = nn2nc_map['map']
    mapped_pe = [] # Stores the layerwise location of pes in theNC mapping neurons

    ## Create source/destination pairs for data transfers
    # Assumption - currently not needed for input layer - input spikes can be broadcasted to any input pe
    ##

    # Populate all src/dest pairs for data transfers in each layer
    d_trans = [] # d_trans - d_transfer
    for idx in xrange(len(net)-1):

        # Initialize src and dest lists for this data-transfer layer
        d_trans.append({'src':[], 'dest':[]})
        d_trans[idx]['src'] = []
        d_trans[idx]['dest'] = []

        # Find src and destinations for this data-transfer layer
        layer_id = idx+1
        out_ng_id = -1 # output neuron group id
        for i in xrange(len(map_t)):
            for j in xrange(len(map_t)):
                for k in xrange(xbar_per_mpe):
                    # check for source - layer_id+1
                    if ((map_t[i,j,k]['layer_id'] == layer_id) and (map_t[i,j,k]['neuron_id'] != 0)):
                        src_pos = {'ncX':i, 'ncY':j, 'pe':k}
                        d_trans[idx]['src'].append(src_pos)
                    if (map_t[i,j,k]['layer_id'] == layer_id+1):
                        dest_pos = {'ncX':i, 'ncY':j, 'pe':k}
                        if (map_t[i,j,k]['neuron_id'] != 0):
                            out_ng_id = out_ng_id + 1
                            d_trans[idx]['dest'].append([]) # append an empty list
                        d_trans[idx]['dest'][out_ng_id].append(dest_pos)

    # Analyze all the data_transfer layers to find local/pw conn for src-dest pairs


# Network & Dataset parameters
inp_size = 28
num_fcl = [[128, 10],
           [256, 10],
           [512, 10],
           [512, 512, 10],
           [1024, 512, 10],
           [1024, 512, 128, 10]]

# Map a neural network to NeuroCell - 2d array of mpes
mapping_list = []
for net in num_fcl:
    dict_temp = {}
    dict_temp['nn'] = net

    # Find ncsize for given network
    nc_size = get_NCsize (net, inp_size)

    # initilize an NC of given size
    NC, last_mapped_mpe = init_NC (nc_size)

    # Assign NN layers (synpases + neurons) to mpes in neurocell
    num_in = pow(inp_size, 2)
    layer_id = 0
    for fcn in net:
        layer_id = layer_id + 1
        num_out = fcn
        NC, last_mapped_mpe = assign_layer2NC (NC, num_in, num_out, layer_id, last_mapped_mpe)
        num_in = num_out

    dict_temp['map'] = NC
    dict_temp['frac_mapped_mpe'] = (len(NC)*last_mapped_mpe['x'] + last_mapped_mpe['y']) / float((len(NC) * len(NC)))
    mapping_list.append(dict_temp)

# Print for sanity check
print ('Number of NNs mapped onto NeuroCell', len(mapping_list))
np.save('nn2nc_map.npy', mapping_list)

### Analyze the mappings
##for i in xrange(len(mapping_list)):
##    map_t = mapping_list[i]
##    connection = analyze_connectivity (map_t)
##    map_t['connection_total'] = connection[0]
##    map_t['connection_local'] = connection[1]
##    # Update the entry with connectivity result
##    mapping_list[i] = map_t
##
##np.save('nn2nc_map.npy', mapping_list)
##print ('Number of NNs analyzed for connectivity', len(mapping_list))
