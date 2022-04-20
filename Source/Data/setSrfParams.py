## Sets Variables for SRF/Stoch Generation

# TYPE:
# 1: point source to point source srf
# 2: point source to finite fault srf
# 3: finite fault to finite fault srf
# 4: multi-segment finite fault srf
TYPE = 2 

# specify basename for gsf, srf and stoch file created
# PREFIX for gsf/srf/stoch files
# if prefix ends with '_', automatic naming follows
PREFIX = 'Srf/Pohang'
# directory for Stoch file(s)
# set to None to not produce the stoch file
STOCH = 'Stoch'

###
### COMMON PARAMETERS (apply to all types but multi)
###

# latitude (float)
LAT = 36.109
# longitude (float)
LON = 129.366
# depth (float)
DEPTH = 7
# magnitude (float)
MAG = 5.4
# strike (int)
STK = 230
# dip (int)
DIP = 69
# rake (int)
RAK = 152
# rupture timestep
DT = 0.01

###
### RELATING TO TYPE 1 (point to point)
###

# specify seismic moment directly (-1 to use magnitude)
MOM = -1

###
### RELATING TO TYPES 2,3,4 (finite fault output)
###
#GENSLIP VERSION:
# '3.3', '5.2.3a'
GENSLIP = '3.3'
# roughness of fault only for genslip 5.0+
# 0.1 is a good value to use - Rob Graves
# 0.0050119 (10^(-2.3)) Shi & Day 2014, default in 5.2.3a
ROUGH = 0.01
RVFRAC = 0.8
SLIP_COV = 0.85
SEED = 103245
# only used in type 4 to go over multiple seeds
SEED_INC = 1

###
### RELATING TO TYPE 2 (centroid moment tensor to finite fault)
###

# Mw Scaling Relation (string), one of:
# HanksBakun2002
# BerrymanEtAl2002
# VillamorEtAl2001
MWSR = 'BerrymanEtAl2002'

###
### RELATING TO TYPE 3 (ffd to finite fault)
###

FLEN = 45.7
DLEN = 0.10
FWID = 45.7
DWID = 0.10
DTOP = 0.0
# km east
SHYPO = 0.0
# km down
DHYPO = 22.8544094807


###
### RELATING TO TYPE 4 (multi-segment finite fault)
###


# how many scenarios to run. different scenarios can have
# randomised parameters (randomisation amount set below)
N_SCENARIOS = 5 
# how many scenarios to run before incrementing the seed value.
# this will randomise parameters but keep the seed the same.
N_SEED_INC = 20
# description of main segments
CASES = ['NNWEpic', 'CharX', 'GrNW', 'GrEW', 'GrEast', 'Horotar', 'NEStepOv']

# master segments can be made up of multiple sub-segments
M_MAG = [5.9, 6.5, 6.4, 6.7, 6.1, 5.9, 3.35]
# as above, if MOM invalid ( <= 0), calculated from MAG
M_MOM = [-1, -1, -1, -1, -1, -1, -1]
# how many segments each master is made of
M_NSEG = [1, 1, 1, 1, 1, 1, 1]

M_SEG_DELAY = ["0", "1", "1", "1", "1", "1", "1"]
M_RVFAC_SEG = ["-1", "0.5", "0.5", "0.5", "0.5", "0.5", "0.5"]
M_GWID = ["-1", "8.0", "8.0", "8.0", "8.0", "8.0", "8.0"]
M_RUP_DELAY = [0, 5, 11.0, 7.0, 18.0, 18.0, 17.0]

# 2 dimentional arrays for each set of segments
# demensions should match MASTER_NSEG
# if values are same, shortcut is [value] * repetitions
M_FLEN = [[8], [10], [16], [20], [14], [7], [11]]
M_DLEN = [ [0.2], [0.2], [0.2], [0.2], [0.2], [0.2], [0.2]]
M_FWID = [[8], [15], [18], [18], [18], [8], [15]]
M_DWID = [ [0.2], [0.2], [0.2], [0.2], [0.2], [0.2], [0.2]]
M_DTOP = [ [2.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0]]
M_STK = [[150], [35], [121], [87], [87], [216], [40]]
M_RAK = [[6], [90], [-180], [180], [180], [78], [171]]
M_DIP = [[54], [70], [105], [80], [78], [50], [80]]
M_ELON = [[172.1811], [172.125], [172.035], [172.195], [172.380], [171.9434], [172.3115]]
M_ELAT = [[-43.5095], [-43.57], [-43.581], [-43.590], [-43.573], [-43.5779], [-43.5509]]
M_SHYPO = [[1], [5], [4], [-1], [-7], [-3.5], [-5.5]]
M_DHYPO = [[4], [10], [6],[6], [6],[4], [6]]

###
### RELATING TO STOCHASTIC GENERATION
###
### set variability, it will change values between scenarios
### length of arrays is same as CASES

# used for calculating M0total in magnitude variability
MW_TOTAL = 7.2
# if multi-segment: relative moment variability
# else: absolute variability
V_MAG = [0.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0]
# fault width/length variability (proportion, eg. 0.1 = 10%)
V_FWID = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
V_FLEN = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
# rupture time delay variability, requires dependency specification below
# absolute value
V_RDELAY = [0, 1, 3, 0.5, 0, 0, 0]
# rupture dependency
# None means it is a starting point
# or 0 -> N-1 (segment which triggers this one)
D_RDELAY = [None, 0, 1, 1, 2, 2, 3]
# hypocentre variabiity - absolute
# for first segment, [SHYPO, DHYPO]
V_HYPO = [1.1, 3]

# TODO: magnitude as a function result if wanted
