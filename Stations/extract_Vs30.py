import rasterio
import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

fname_dataset = r"/scratch/x2319a02/gmsim/Busan_Data/global_vs30.tif"


def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("fname_ll",type=str,help="stat file ll")

    args = parser.parse_args()
    return args

args=load_args()

#fname_ll = r"./Busan_2km_stats_20220314.ll"
#fname_vs30 = r"./Busan_2km_stats_20220314.vs30"
fname_ll = Path(args.fname_ll)
print(f"input .ll file: {fname_ll}")
assert(fname_ll.exists())
fname_vs30=fname_ll.with_suffix('.vs30')
print(f"output .v30 file: {fname_vs30}")

#ll = np.genfromtxt(fname_ll, delimiter=' ', dtype=None)
ll = np.genfromtxt(fname_ll, delimiter=' ', dtype=None)

n_sta = len(ll)

dataset = rasterio.open(fname_dataset)
band1 = dataset.read(1)

lat_sta = []
lon_sta = []
code_sta = []
vs30_sta = []

for ind, sta in enumerate(ll):
    #lon_sta[ind] = sta[0]
    #lat_sta[ind] = sta[1]
    #code_sta[ind] = sta[2]
    lon_sta.append(sta[0])
    lat_sta.append(sta[1])
    code_sta.append(sta[2])
    row, col = dataset.index(sta[0], sta[1])
    vs30_sta.append(band1[row, col])

# generate vs30 input file
vs30file = open(fname_vs30, 'w')
for code, vs30 in zip(code_sta, vs30_sta):
    vs30file.writelines(code.decode() + ' ' + str(vs30) + '\n')
vs30file.close()

# plot vs30 scatter plot
fig0 = plt.figure(figsize=(6,6))
ax0 = fig0.gca()
im0 = ax0.scatter(lon_sta, lat_sta, s=1, c=vs30_sta)
ax0.set_xlabel('Lon [deg]')
ax0.set_ylabel('Lat [deg]')
cbar = plt.colorbar(im0)
cbar.set_label('Vs30 [m/s]')
plt.tight_layout()
