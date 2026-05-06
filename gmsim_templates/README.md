The ground motion simulation versions found here are available in a larger format here: https://wiki.canterbury.ac.nz/display/QuakeCore/Simulation
The final suffix of .4, .2 or .1 denotes the grid spacing used of 400m, 200m or 100m

#Version 16.1
    - HF: v5.4.5
    - path_dur: 1
    - fmin: 0.2
    - fmidbot: 0.5
    - lsvsref: 500.0
    
#Version 18.5.3
#####Similar to 16.1
    - HF: v5.4.5.1
    - path_dur: 11
    - fmin: 0.5
    - fmidbot: 1.0
    - no-lf-amp: True

#Version 18.5.4
#####Similar to 18.5.3
    - HF: v5.4.5.2
    
#Version 20.1.1
#####Similar to 18.5.3
    - HF: v5.4.6.1
    
#Version 20.1.2
#####Similar to 18.5.4
    - HF: v5.4.6.2
    
#Version 20.4.1.4
#####Similar to 18.5.3
    - hb_high version = 5.4.5.3_new_gnu
    - czero = 2.0
    - rvfac_shal = 0.6
    - rvfac_deep = 0.6
    - emod3d version = 3.0.8
    - rayset 1
    - Added pSA periods, default in this version is now 31 periods 

#Version 20.4.1.2
#####Similar to 20.4.1.4
    - flo: 0.5
    - dt: 0.01
    - fmin: 0.25
    - fmidbot: 0.5 

