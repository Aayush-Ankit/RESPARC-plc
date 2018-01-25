import matplotlib.pyplot as plt
import numpy as np

# Extract data
mapping_list = np.load('nn2nc_map.npy')
conn_total = []
conn_local = []
conn_pwl = []
for map_t in mapping_list:
    total = float(map_t['connection_total'])
    local = float(map_t['connection_local'])
    pwl =  total - local
    conn_total.append(total)
    conn_local.append(local / total)
    conn_pwl.append(pwl / total)


N = len(conn_local)
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

# Plot connectivity distribution data
##p1 = plt.bar(ind, conn_local, width, color=(0.2588,0.4433,1.0),
##             label = 'Local')
##p2 = plt.bar(ind, conn_pwl, width, color=(1.0,0.5,0.62),
##             label = 'Powerline',
##             bottom=conn_local)
##plt.ylim([0,1.2])
##plt.ylabel('Data transfers per timestep of SNN computation')
##plt.xlabel('Neural Networks (Increasing size Left to Right)')
##plt.title('Connectivity distribution within NeuroCell')
##plt.legend()
##
##plt.savefig('connectivity_distribution.png')

# Plot total connectivity data
p3 = plt.bar(ind, conn_total, width, color=(0.2588,0.4433,1.0),
             label = 'Local')
plt.ylabel('Total Number of Connections')
plt.xlabel('Neural Networks (Increasing size Left to Right)')
plt.title('Total Connectivity reqjuired within NeuroCell')

plt.savefig('connectivity_analysis.png')
