# script to compute energy for different benchmarks
# components - compute, intra-layer data transfer, inter-layer data transfer

from math import *

# compute neurocell size for the network
def get_nc_size (net, xbar_size, num_xbar_per_pe, xbar_replication, out_size, ker_size, ss_size):
    num_pe = 0
    for i in range (len(net)-1):
        # CNN layer
        if (i != len(net)-2):
            # number of compute operations
            logical_xbar_size = [net[i]*ker_size*ker_size, net[i+1]]
            num_xbar = ceil (logical_xbar_size[0]/xbar_size) * ceil (logical_xbar_size[1]/xbar_size)
            num_pe = num_pe + ceil(num_xbar*xbar_replication / num_xbar_per_pe)
        # FC layer
        else:
            # number of compute operations
            logical_xbar_size = [net[i]*(out_size[i-1]/ss_size)**2, net[i+1]]
            num_xbar = ceil (logical_xbar_size[0]/xbar_size) * ceil (logical_xbar_size[1]/xbar_size)
            num_pe = num_pe + ceil(num_xbar/num_xbar_per_pe)

    return ceil(sqrt(num_pe))

# CNN configurations
ker_size = 5
ss_size = 2
out_size = [[24, 8],
           [28, 10],
           [28, 10]]
cnn_net = [[1, 12, 32, 10], #1x28x28 - 12c5 - 2s - 32c5 - 10
           [1, 12, 64, 10], #1x32x32 - 12c5 - 2s - 64c5 - 10
           [1, 24, 64, 10]] #1x32x32 - 24c5 - 2s - 64c5 - 10


# arch configs
xbar_size = 64.0
num_xbar_per_pe = 4.0
noc_conc = 4.0
vmem_precision = 4 # bits
# max neuron fan in for one hop intra-layer data transfer
max_fan_in = 2*xbar_size * num_xbar_per_pe * noc_conc
flit_width = 16 # bits
packet_width = 128 # bits
xbar_replication = 64 #xbars in CNN layers have been replicated 100X to sustain throughput

# power (mw), area (mm2) and latency (ns) numbers (from excel sheet - resparc_model/resparc-plc-area-power)
compute_pow = 3.0187
compute_area = 0.0196
compute_lat = 100

router_pow = 23.1/noc_conc # per PE
router_area = 0.0259/noc_conc # per PE
router_lat = 1

link_pow = 3/noc_conc # per PE
link_area = 0.00996/noc_conc # per PE
link_lat = 1

# noc packet latency for corresponding NC sizes of networks - from booksim traces
noc_average_latency = {'2':14.86, '4':22.47,
                       '6':27.68, '8':34.19,
                       '10':40.25, '12':47.56,
                       '14':57.29, '16':67.72, '18':92.79}

noc_average_hop = {'2':1.0, '4':2.06,
                   '6':2.75, '8':3.51,
                   '10':4.21, '12':4.81,
                   '14':5.54, '16':6.21, '18':6.91}


# compute number of accesses (compute, intra-data transferm inter-data transfer) for a net
num_compute = []
num_intra = []
num_inter = []
nc_size = []
num_hop = [] #layer-wise max hop of each net

for j in range(len(cnn_net)):
    # print ('computing energy for net: ', mlp_net[j])
    num_compute.append(0)
    num_intra.append(0)
    num_inter.append(0)
    nc_size_temp = get_nc_size (cnn_net[j], xbar_size, num_xbar_per_pe, xbar_replication, out_size[j], ker_size, ss_size)
    nc_size.append(nc_size_temp)
    num_hop_net = []

    for i in range(len(cnn_net[j])-1):
        #print ('computing layer ' + str(i) + '......')

        # number of computation in a layer
        # CNN layer
        if (i != len(cnn_net[j])-2):
            logical_xbar_size = [cnn_net[j][i]*ker_size*ker_size, cnn_net[j][i+1]]
            num_xbar = ceil (logical_xbar_size[0]/xbar_size) * ceil (logical_xbar_size[1]/xbar_size)
            num_compute[j] = num_compute[j] + num_xbar * (out_size[j][i]**2)
        # FC layer
        else:
            logical_xbar_size = [cnn_net[j][i]*((out_size[j][i-1]/ss_size)**2), cnn_net[j][i+1]]
            num_xbar = ceil (logical_xbar_size[0]/xbar_size) * ceil (logical_xbar_size[1]/xbar_size)
            num_compute[j] = num_compute[j] + num_xbar


        # number of intra-transfers (within a layer)
        # xbar allocation strategy -> xbars which lead to same output are colocated in a PE,
        # One PE maps only one 128 group of output neuron
        # assume all intra-layer data transfers use zero hop between routers only (i.e. all connected to one router)
        # CNN layer
        if (i != len(cnn_net[j])-2):
            assert (cnn_net[j][i]*ker_size*ker_size <= max_fan_in), 'neuron fan-in exceeds satisfy zero hop constraint'
            num_intra_per_output = ceil(log(ceil(logical_xbar_size[0]/xbar_size), 2)) * ceil(logical_xbar_size[1]/xbar_size)
            num_intra[j] = num_intra[j] + num_intra_per_output * (out_size[j][i]**2)
        # FC layer
        else:
            assert (cnn_net[j][i]*((out_size[j][i-1]/ss_size)**2) <= max_fan_in), 'neuron fan-in exceeds satisfy zero hop constraint'
            num_intra[j] = num_intra[j] + ceil(log(ceil(logical_xbar_size[0]/xbar_size), 2))


        # number of inter-transfers (between layers)
        # layers are mapped column major wise on 2-d PE array - assumed for simple mapping
        # layer 1 receives inputs from  fixed source (dummy PE for eg. PE0, this PE gets data dump from host)
        # each xbar mapped to this layer will receive an input data packet from previous layer
        # num_in_col and num_out_col are used to calculate an estimate of hops for the inter-layer data transfer
        # num_in_col is the number of columns mapped to the previous layer xbars
        # num_out_col is the number of columns mapped to the current layer xbars
        # number of intervening columns between an input and output column is used to estimate number of hop
        # Col1 -router- Col2 -router- Col3 -router- Col4
        # CNN layer
        if (i != len(cnn_net[j])-2):
            num_out_col = ceil((num_xbar*xbar_replication) / (num_xbar_per_pe*nc_size_temp))
            if (i != 0):
                num_xbar_prev = ceil (cnn_net[j][i-1]*ker_size*ker_size/xbar_size) * ceil (cnn_net[j][i]/xbar_size)
                num_in_col = ceil((num_xbar_prev*xbar_replication) / (num_xbar_per_pe*nc_size_temp))
            else:
                num_in_col = 1

            max_hop = num_in_col + num_out_col - 1
            min_hop = num_in_col
            avg_hop = (max_hop + min_hop)/2.0
            num_hop_net.append(avg_hop)
            # number of data transfers between layer - input map size (in_map * in_size^2) * ker_size
            # each input can be used for upto ker_size
            temp = num_inter[j]
            num_inter[j] = num_inter[j] + (cnn_net[j][i] * ((out_size[j][i]+ker_size-1)**2) * ker_size) * avg_hop
        # FC layer
        else:
            # last layer is FC
            num_out_col = ceil(num_xbar / (num_xbar_per_pe*nc_size_temp))
            # prev layer was conv
            num_xbar_prev = ceil (cnn_net[j][i-1]*ker_size*ker_size/xbar_size) * ceil (cnn_net[j][i]/xbar_size)
            num_in_col = ceil((num_xbar_prev*xbar_replication) / (num_xbar_per_pe*nc_size_temp))

            temp = num_inter[j]
            max_hop = num_in_col + num_out_col - 1
            num_hop_net.append(max_hop)
            for x in range(int(num_out_col)):
                for y in range(int(num_in_col)):
                    num_inter[j] = num_inter[j] + ceil((num_xbar/(num_out_col*num_in_col))) * (x+y+1)

    num_hop.append(num_hop_net)

    # print stats for the network
    #print ('num_compute', num_compute[j])
    #print ('nc_size', nc_size[j])
    #print ('num_intra', num_intra[j])
    #print ('num_hop', num_hop[j])
    #print ('num_inter', num_inter[j])
    #print ('\n')


# compute energy components from access - format (compute, intra, inter, tot)
energy = []
for j in range(len(cnn_net)):
    #print ('computing energy for net: ', mlp_net[j])
    energy_temp = []

    # computation energy (in PE)
    # num_pe * (pe_pow) * (pe_lat)
    num_pe = (num_compute[j]/num_xbar_per_pe)
    energy_compute = num_pe * compute_pow * compute_lat # in nJ
    energy_temp.append(energy_compute)

    # intra-layer data transfer energy (for vmem accumulation)
    # num_packets per intra-transfer * (router_pow+link_pow) * latency of oen packet through one router (2*2 NC)
    num_packets = xbar_size * vmem_precision / packet_width
    single_packet_intra_lat = noc_average_latency['2'] / noc_average_hop['2']
    energy_intra = num_intra[j] * num_packets * (router_pow + link_pow) * single_packet_intra_lat # in nJ
    energy_temp.append(energy_intra)

    # inter-layer data transfer energy (for spike transfers)
    num_packets = 1.0 / packet_width
    nc_size_temp = int(ceil((nc_size[j]/2.0))*2)
    packet_lat_per_hop = noc_average_latency[str(nc_size_temp)] / noc_average_hop[str(nc_size_temp)]
    energy_inter = num_inter[j] * num_packets * (2*router_pow + link_pow) * packet_lat_per_hop # in nJ
    energy_temp.append(energy_inter)

    energy_tot = energy_compute + energy_intra + energy_inter
    energy_temp.append(energy_tot)

    energy.append(energy_temp)


# Analyze energy profile
print ('energy analysis:')
for j in range(len(cnn_net)):
    comp_frac = energy[j][0] / energy[j][3] * 100
    intra_frac = energy[j][1] / energy[j][3] * 100
    inter_frac = energy[j][2] / energy[j][3] * 100

    print ('comp_frac: ' + str(comp_frac) + ' ' +
           'intra_frac: ' + str(intra_frac) + ' ' +
           'inter_frac: ' + str(inter_frac))


# compute inference latency from access components
compute_latency = []
intra_latency = []
inter_latency = []
total_latency = []

for j in range(len(cnn_net)):

    # add layer-wise latency
    compute_latency.append(0)
    intra_latency.append(0)
    inter_latency.append(0)
    total_latency.append(0)

    for i in range(len(cnn_net[j])-1):

        # compute latency for one convolution, intra-transfer and its inter transfer
        # Assumption: convolutions have been unrolled in area by xbar replication
        # Even for multiple successive convolutions using same xbar, relative distribution of compute, intra and inter
        # remain same
        compute_latency_temp = compute_lat

        # intra data transfer latency
        num_packets = xbar_size * vmem_precision / packet_width
        single_packet_intra_lat = noc_average_latency['2'] / noc_average_hop['2']

        if (i != len(cnn_net[j])-2):
            logical_xbar_size = [cnn_net[j][i]*ker_size*ker_size, cnn_net[j][i+1]]
        else:
            logical_xbar_size = [cnn_net[j][i]*((out_size[j][i-1]/ss_size)**2), cnn_net[j][i+1]]

        num_reduction_stages = ceil(log(ceil(logical_xbar_size[0]/xbar_size), 2))
        intra_latency_temp = num_packets * single_packet_intra_lat * num_reduction_stages

        # inter data transfer latency
        nc_size_temp = int(ceil((nc_size[j]/2.0))*2)
        packet_lat_per_hop = noc_average_latency[str(nc_size_temp)] / noc_average_hop[str(nc_size_temp)]
        inter_latency_temp = packet_lat_per_hop * num_hop[j][i]

        total_latency_temp =  (compute_latency_temp + intra_latency_temp + inter_latency_temp)

        compute_latency[j] = compute_latency[j] + compute_latency_temp
        intra_latency[j] = intra_latency[j] + intra_latency_temp
        inter_latency[j] = inter_latency[j] + inter_latency_temp
        total_latency[j] = total_latency[j] + total_latency_temp


# Analyze latency profile
print ('\nlatency analysis:')
for j in range(len(cnn_net)):
    comp_frac = compute_latency[j] / total_latency[j] * 100
    intra_frac = intra_latency[j] / total_latency[j] * 100
    inter_frac = inter_latency[j] / total_latency[j] * 100

    print ('comp_frac: ' + str(comp_frac) + ' ' +
           'intra_frac: ' + str(intra_frac) + ' ' +
           'inter_frac: ' + str(inter_frac))

