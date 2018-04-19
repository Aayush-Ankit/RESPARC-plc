# Compute the energy for NN implementations on NeuroCell
# Components: Computation, Control, Communication
# Computation - MCA, Neuron
# Communication - Local (Switch), Powerline
# Peripheral - Input & Output Buffer
# Control - Ignored for now

import math
import numpy as np

# general constants
mw = pow(10, -3)
nj = pow(10, -9)
ns = pow(10, -9)
pj = pow(10, -12)
kohm = pow(10, 3)
vdd = 1

# xbar related constants
xbar_size = 64
xbar_per_mpe = 4
v_mca = vdd/2
g_min = 1/(20*kohm)
g_max = 1/(200*kohm)
g_avg = (g_min + g_max)/2

# other implementation parameters
v_overscale = True
v_scale = pow(0.7, 2) if v_overscale else 1
cycle_time = 5*ns

# syntehsis parameters (from min/a/aankit/ReSpArch.../Matlab/energy_vary_scrossbar_size.m)
switch_energy = 2 * (0.231*mw * cycle_time) * v_overscale # 2 cycles for receive & send
pwl_tx_energy =
pwl_rx_energy = 
buff_write_energy = (0.28*0.6)*mw * cycle_time * v_overscale
neuron_energy = 2*pj  * 45/65
mca_read_energy = pow(xbar_size,2) * pow(v_mca,2) * g_avg

# simulation parameters
spike_probability = 0.7

# Compute for all topologies
mapping_list = np.load('nn2nc_map.npy')
energy_list = []
for map_t in mapping _list:
    dict_temp = {}
    dict_temp['mca_energy'] =  (sum(sum(map_t['map'] != 0)) * xbar_per_mpe * mca_read_energy) *
                                spike_probability
    dict_temp['neuron_energy'] =  (sum(map_t['nn']) * neuron_energy) *
                                   spike_probability
    input_buffer_energy = (sum(sum(map_t['map'] != 0)) * xbar_per_mpe)
                            * buff_write_energy * v_scale
    output_buffer_energy = np.ceil(sum(map_t['nn']) / float(xbar_size))
                            * buff_write_energy * v_scale
    dict_temp['buffer'] = input_buffer_energy + output_buffer_energy

    # Factor of 2 - in typical/worst case a local transfer will involve 2 switches
    dict_temp['local_conn'] = (2*map_t['connection_local']) * switch_energy * v_scale

    pwl_conn = map_t['connection_total'] - map_t['connection_local']
    addr_bits = 2 + 2 + math.log(2*len(map_t['map']) - 1)
    # number of bits in a spike packet
    num_bits = addr_bits + xbar_size
    dict_temp['pwl_conn'] = pwl_conn * num_bits * (# Find the number of broadcasts - rxs in each broadcast)   



