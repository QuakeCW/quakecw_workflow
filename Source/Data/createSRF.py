#!/usr/bin/env python3

import math
import os
from logging import Logger
from shutil import copyfile
from subprocess import call, PIPE, Popen
import sys
from random import randint

from h5py import File as h5open
import numpy as np

from qcore import geo, srf, binary_version, qclogging, utils

# local srf_config has a higher priority
sys.path.append(os.path.abspath(os.curdir))
import srf_config

SRF2STOCH = "srf2stoch"
GENERICSLIP2SRF = "generic_slip2srf"
FAULTSEG2GSFDIPDIR = "fault_seg2gsf_dipdir"


def get_seed():
    """Returns a seed in the range of 0 to the largest 4 byte signed int possible in C"""
    return randint(0, 2 ** 31 - 1)


def mkdir_p(out_dir, logger: Logger = qclogging.get_basic_logger()):
    logger.debug("Making directory {}".format(out_dir))
    if out_dir != "" and not os.path.isdir(out_dir):
        try:
            os.makedirs(out_dir)
        except OSError:
            if not os.path.exists(out_dir):
                logger.log(
                    qclogging.NOPRINTERROR,
                    "OSError occured, unable to make directory. Exiting",
                )
                raise
            logger.log(
                qclogging.NOPRINTCRITICAL,
                "OSError was raised, but directory exists, continuing",
            )


def srf_join(in1, in2, out):
    """
    like srf_join.c but that wasn't working properly
    """
    with open(in1, "r") as f1:
        s1 = f1.readlines()
    with open(in2, "r") as f2:
        s2 = f2.readlines()
    o = open(out, "w")

    # must be the same version
    assert s1[0] == s2[0]
    o.write(s1[0])

    # planes - header
    p1 = int(s1[1].split()[1])
    p2 = int(s2[1].split()[1])
    o.write("PLANE %d\n" % (p1 + p2))
    q1 = 2 + p1 * 2
    q2 = 2 + p2 * 2
    # planes - content
    o.write("".join(s1[2:q1]))
    o.write("".join(s2[2:q2]))

    # points - header
    o.write("POINTS %d\n" % (int(s1[q1].split()[1]) + int(s2[q2].split()[1])))
    # points - rest of file
    o.write("".join(s1[q1 + 1 :]))
    o.write("".join(s2[q2 + 1 :]))

    o.close()


mag2mom = lambda mw: math.exp(1.5 * (mw + 10.7) * math.log(10.0))
mom2mag = lambda mom: (2 / 3.0 * math.log(mom) / math.log(10.0)) - 10.7
get_nx = lambda FLEN, DLEN: "%.0f" % (FLEN / DLEN)
get_ny = lambda FWID, DWID: "%.0f" % (FWID / DWID)
get_fileroot = lambda MAG, FLEN, FWID, seed: "m%.2f-%.1fx%.1f_s%d" % (
    MAG,
    FLEN,
    FWID,
    seed,
)
get_gsfname = lambda MAG, DLEN, DWID: "m%.2f-%.2fx%.2f.gsf" % (MAG, DLEN, DWID)
# Leonard 2014 Relations
def leonard(rake, A, ds=4.00, ss=3.99):
    # if dip slip else strike slip
    if round(rake % 360 / 90.0) % 2:
        return ds + math.log10(A)
    else:
        return ss + math.log10(A)


def skarlatoudis(A):
    return math.log10(A) - (math.log10(1.77 * math.pow(10, -10)) + 6.03)


# by earth radius
# not really correct for NZ, use proper formulas
one_deg_lat = math.radians(6371.0072)

# comment placed in corners file (above/below hypocenter)
# make sure lines end with '\n', especially the last one.
corners_header = (
    "> header line here for specifics \n\
> This is the standard input file format where the \
hypocenter is first then for each \n\
>Hypocenter (reference??) \n",
    "> Below are the corners \
(first point repeated as fifth to close box \n",
)


def write_corners(filename, hypocentre, corners):
    """
    Write a corners text file (used to plot faults).
    """
    with open(filename, "w") as cf:
        # lines beginning with '>' are ignored
        cf.write(corners_header[0])
        cf.write("%f %f\n" % (hypocentre))
        cf.write(corners_header[1])
        # 0 1 - draw in order to close box
        # 2 3
        for i in [0, 1, 3, 2, 0]:
            cf.write("%f %f\n" % tuple(corners[i]))


def get_corners(lat, lon, flen, fwid, dip, strike):
    """
    Return Corners of a fault. Indexes are as below.
    0 1
    2 3
    """
    # use cartesian coordinate system to define the along strike and downdip
    # locations taking the center of the fault plane as (x,y)=(0,0)
    xPos = np.array([-flen / 2.0, flen / 2.0])
    yPos = np.array([-fwid, 0.0])
    Nx = len(xPos)
    Ny = len(yPos)

    # now use a coordinate transformation to go from fault plane to North and
    # East cartesian plane (again with (0,0) ==(0,0)  )
    yPosSurfProj = yPos * math.cos(math.radians(dip))
    azimuth = math.radians(strike - 90)
    RotMatrix = np.array(
        [
            [math.cos(azimuth), math.sin(azimuth)],
            [-math.sin(azimuth), math.cos(azimuth)],
        ]
    )
    eastLocRelative, northLocRelative = np.dot(
        RotMatrix, [np.tile(xPos, Ny), yPosSurfProj.repeat(Ny)]
    ).reshape(2, Nx, Ny)

    # now use a coordinate transformation to go from the North East cartesian
    # plane to the spherical earth WGS84 coordinate system
    lats = lat + northLocRelative / one_deg_lat
    lons = lon + (eastLocRelative / one_deg_lat) * 1 / math.cos(math.radians(lat))

    # joined (lon, lat) pairs
    return np.dstack((lons.flat, lats.flat))[0]


def get_hypocentre(lat, lon, flen, fwid, shypo, dhypo, strike, dip):
    """
    Same logic as corners, for a single point.
    """
    y_pos_surf_proj_hyp = -dhypo * math.cos(math.radians(dip))

    azimuth = math.radians(strike - 90)
    rot_matrix = np.array(
        [
            [math.cos(azimuth), math.sin(azimuth)],
            [-math.sin(azimuth), math.cos(azimuth)],
        ]
    )
    A = np.dot(rot_matrix, [[shypo], [y_pos_surf_proj_hyp]])

    lat_hyp = lat + A[1][0] / one_deg_lat
    lon_hyp = lon + (A[0][0] / one_deg_lat) * 1.0 / (math.cos(math.radians(lat)))

    return lon_hyp, lat_hyp


def focal_mechanism_2_finite_fault(
    Lat, Lon, Depth, Mw, strike, rake, dip, MwScalingRel
):
    """
    Purpose: To create a finite fault geometry based on centroid moment tensor
    solution information and magnitude scaling relationships.
    The use of such finite fault geometry is for first order computation of
    source-to-site distances.

    revisions
    v2 - reoriented fault plane to be consistent with along strike direction
    v3 - added 'argout_emod3d' output and associated commands to output details
         which are input in the finite fault model generation for EMOD3D graves methodology

    assumptions:
    1) The centroid moment tensor represents the centroid of the fault plane,
    located half way along strike and downdip
    2) The fault area is computed from the median of a Moment scaling
    relationship and thus is assumed to be a 'typical' stress drop event for
    the Mw-relationship used.
    Should only be used for small events where the downdip width is smaller
    than the seismogenic depth (i.e. so the assumption of a square fault plane
    is reasonable); depth is reset to zero if above ground values determined
    3) srike in deg measured clockwise from N; rake in deg measured
    anti-clockwise from the strike direction (and in the range
    -180<lambda<180; dip in deg measured downward from horizontal

    Input variables:
    Lat    - the latitude of the focal mechanism (-ve below equator)
    Lon    - the lon of the focal mech (-180<lon<180)
    Depth  - the depth of the focal mech (in km)
    Mw     - the moment magnitude from the Mw tensor soln
    strike - the strike of the focal mech (only 1)
    rake   - rake (not used, but carried forward)
    dip    - the dip angle of the fault plane

    output variables:
    lat       - the latitude of the subfault
    lon       - the lon of the subfault
    depth     - depth of the subfault
    lonAsList - as a 1D array
    """

    # fixed values
    DLEN = 0.1
    DWID = 0.1
    SHYPO = 0.00

    # get the fault geometry (square edge length)
    fault_length, fault_width = MwScalingRelation(Mw, MwScalingRel, rake)
    # number of subfaults
    Nx = int(round(fault_length / DLEN))
    Ny = int(round(fault_width / DWID))
    # rounded subfault spacing
    DLEN = fault_length / float(Nx)
    DWID = fault_width / float(Ny)

    # use cartesian coordinate system to define the along strike and downdip
    # locations taking the center of the fault plane as (x,y)=(0,0)
    xPos: np.ndarray = np.arange(DLEN / 2.0, fault_length, DLEN) - fault_length / 2.0
    yPos: np.ndarray = (
        np.arange(DWID / 2.0, fault_width, DWID)[::-1] - fault_width / 2.0
    )

    # now use a coordinate transformation to go from fault plane to North and
    # East cartesian plane (again with (0,0) ==(0,0)  )
    yPosSurfProj = yPos * math.cos(math.radians(dip))
    rotAngleAzimuth = math.radians(strike - 90)
    RotMatrix = np.array(
        [
            [math.cos(rotAngleAzimuth), math.sin(rotAngleAzimuth)],
            [-math.sin(rotAngleAzimuth), math.cos(rotAngleAzimuth)],
        ]
    )
    eastLocRelative, northLocRelative = np.dot(
        RotMatrix, [np.tile(xPos, Ny), yPosSurfProj.repeat(Ny)]
    ).reshape((2, Nx, Ny))
    depthLocRelative = (
        (-yPos * math.sin(math.radians(dip))).repeat(Ny).reshape((Nx, Ny))
    )

    # now use a coordinate transformation to go from the North East cartesian
    # plane to the spherical earth WGS84 coordinate system
    lats = Lat + northLocRelative / one_deg_lat
    lons = Lon + (eastLocRelative / one_deg_lat) * 1 / math.cos(math.radians(Lat))
    depths = np.maximum(Depth + depthLocRelative, 0)

    # determine topcenter of the fault plane (top edge, center point along strike)
    # see note at top for V3 changes.  "tcl" means "topcenter location"
    xPos_tcl = 0
    yPos_tcl = fault_width / 2.0
    # convert to NE system
    yPosSurfProj_tcl = yPos_tcl * math.cos(math.radians(dip))
    A = np.dot(RotMatrix, [[xPos_tcl], [yPosSurfProj_tcl]])
    eastLocRelative_tcl = A[0][0]
    northLocRelative_tcl = A[1][0]
    depthLocRelative_tcl = -yPos_tcl * math.sin(math.radians(dip))
    # convert to Lat, Lon, depth
    lat_tcl = Lat + northLocRelative_tcl / one_deg_lat
    lon_tcl = Lon + (eastLocRelative_tcl / one_deg_lat) * 1 / math.cos(
        math.radians(Lat)
    )
    depth_tcl = max([Depth + depthLocRelative_tcl, 0])

    DHYPO = fault_width / 2.0
    return (
        lats,
        lons,
        depths,
        fault_length,
        DLEN,
        fault_width,
        DWID,
        depth_tcl,
        lat_tcl,
        lon_tcl,
        SHYPO,
        DHYPO,
    )


###########################################################################
def MwScalingRelation(
    Mw,
    MwScalingRel,
    rake=None,
    leonard_ds=4.00,
    leonard_ss=3.99,
    logger: Logger = qclogging.get_basic_logger(),
):
    """
    Return the fault Area from the Mw and a Mw Scaling relation.
    """
    if MwScalingRel == "HanksBakun2002":
        try:
            # only small magnitude case
            assert Mw <= 6.71
        except AssertionError as e:
            logger.log(
                qclogging.NOPRINTERROR,
                "Cannot use HanksBakun2002 scaling relation for Mw = {} > 6.71".format(
                    Mw
                ),
            )
            e.args += ("Cannot use HanksAndBakun2002 equation for Mw > 6.71",)
            raise
        A = 10 ** (Mw - 3.98)

    elif MwScalingRel == "BerrymanEtAl2002":
        A = 10 ** (Mw - 4.18)
        # i.e. set L=W=sqrt(A) in Eqn 1 in [1] Stirling, MW, Gerstenberger, M, Litchfield, N, McVerry, GH, Smith, WD, Pettinga, JR, Barnes, P. 2007.
        # updated probabilistic seismic hazard assessment for the Canterbury region, GNS Science Consultancy Report 2007/232, ECan Report Number U06/6. 58pp.

    elif MwScalingRel == "VillamorEtAl2001":
        A = 10 ** (0.75 * (Mw - 3.39))
        # i.e. Eqn 2 in [1] Stirling, MW, Gerstenberger, M, Litchfield, N, McVerry, GH, Smith, WD, Pettinga, JR, Barnes, P. 2007.
        # updated probabilistic seismic hazard assessment for the Canterbury region, GNS Science Consultancy Report 2007/232, ECan Report Number U06/6. 58pp.

    elif MwScalingRel == "Leonard2014":
        if round(rake % 360 / 90.0) % 2:
            A = 10 ** (Mw - leonard_ds)
        else:
            A = 10 ** (Mw - leonard_ss)

    else:
        raise ValueError("Invalid MwScalingRel: {}. Exiting.".format(MwScalingRel))

    # length, width
    logger.debug(
        "MwScalingRel {} determined a fault area of {} square kilometres".format(
            MwScalingRel, A
        )
    )
    return math.sqrt(A), math.sqrt(A)


def gen_gsf(
    gsf_file,
    lon,
    lat,
    dtop,
    strike,
    dip,
    rake,
    flen,
    fwid,
    nx,
    ny,
    logger: Logger = qclogging.get_basic_logger(),
):
    logger.debug("Saving gsf to {}".format(gsf_file))
    with open(gsf_file, "w") as gsfp:
        gexec = Popen(
            [
                binary_version.get_unversioned_bin(FAULTSEG2GSFDIPDIR),
                "read_slip_vals=0",
            ],
            stdin=PIPE,
            stdout=gsfp,
        )
        gexec.communicate(
            "1\n{:f} {:f} {:f} {} {} {} {:f} {:f} {:s} {:s}".format(
                lon, lat, dtop, strike, dip, rake, flen, fwid, nx, ny
            ).encode("utf-8")
        )
        gexec.wait()


def gen_srf(
    srf_file,
    gsf_file,
    mw,
    dt,
    nx,
    ny,
    seed,
    shypo,
    dhypo,
    genslip_version="3.3",
    rvfrac=None,
    rough=None,
    slip_cov=None,
    velocity_model=None,
    logger: Logger = qclogging.get_basic_logger(),
):
    if velocity_model is None:
        logger.debug(
            "Velocity model not explicitly provided, using value from srf config"
        )
        velocity_model = srf_config.VELOCITY_MODEL
    logger.debug("Velocity model: {}".format(velocity_model))

    with open(srf_file, "w") as srfp:
        genslip_bin = binary_version.get_genslip_bin(genslip_version)
        if int(genslip_version[0]) < 5:
            logger.debug(
                "Using genslip version {}. Using nxand ny".format(genslip_version)
            )
            xstk = "nx"
            ydip = "ny"
        else:
            logger.debug(
                "Using genslip version {}. Using nstk and ndip".format(genslip_version)
            )
            xstk = "nstk"
            ydip = "ndip"
        cmd = [
            genslip_bin,
            "read_erf=0",
            "write_srf=1",
            "read_gsf=1",
            "write_gsf=0",
            "infile=%s" % (gsf_file),
            "mag=%f" % (mw),
            "%s=%s" % (xstk, nx),
            "%s=%s" % (ydip, ny),
            "ns=1",
            "nh=1",
            "seed=%d" % (seed),
            "velfile=%s" % (velocity_model),
            "shypo=%f" % (shypo),
            "dhypo=%f" % (dhypo),
            "dt=%f" % dt,
            "plane_header=1",
            "srf_version=1.0",
        ]
        if rvfrac is not None:
            cmd.append("rvfrac=%s" % (rvfrac))
        if rough is not None:
            cmd.append("alpha_rough=%s" % (rough))
        if slip_cov is not None:
            cmd.append("slip_sigma=%s" % (slip_cov))
        logger.info("Creating SRF with command: {}".format(" ".join(cmd)))
        call(cmd, stdout=srfp)


def gen_stoch(
    stoch_file,
    srf_file,
    silent=False,
    single_segment=False,
    logger: Logger = qclogging.get_basic_logger(),
):
    """
    Creates stoch file from srf file.
    """
    logger.debug("Generating stoch file: {}".format(stoch_file))
    out_dir = os.path.dirname(stoch_file)
    mkdir_p(out_dir, logger=logger)
    stderr = None
    if silent:
        stderr = PIPE
    dx, dy = 2.0, 2.0
    if not srf.is_ff(srf_file):
        dx, dy = srf.srf_dxy(srf_file)
    with open(stoch_file, "w") as stochp, open(srf_file, "r") as srfp:
        if single_segment:
            logger.debug(
                "Fault is single segment, passing target_dx, target_dy. Stdin file: {}".format(
                    srfp
                )
            )
            call(
                [
                    binary_version.get_unversioned_bin(SRF2STOCH),
                    "target_dx={}".format(dx),
                    "target_dy={}".format(dy),
                ],
                stdin=srfp,
                stdout=stochp,
            )
        else:
            logger.debug(
                "Fault is multi segment, passing dx, dy. Stdin file: {}".format(srfp)
            )
            call(
                [
                    binary_version.get_unversioned_bin(SRF2STOCH),
                    "dx={}".format(dx),
                    "dy={}".format(dy),
                ],
                stdin=srfp,
                stdout=stochp,
            )


def gen_meta(
    srf_file,
    srf_type,
    mag,
    strike,
    rake,
    dip,
    dt,
    vm=None,
    vs=None,
    rho=None,
    centroid_depth=None,
    lon=None,
    lat=None,
    mom=None,
    flen=None,
    dlen=None,
    fwid=None,
    dwid=None,
    shypo=None,
    dhypo=None,
    mwsr=None,
    tect_type=None,
    dip_dir=None,
    file_name=None,
    logger: Logger = qclogging.get_basic_logger(),
):
    """
    Stores SRF metadata as hdf5.
    srf_file: SRF path used as basename for info file and additional metadata
    """
    logger.debug("Generating srf info file")
    planes = srf.read_header(srf_file, idx=True)
    hlon, hlat, hdepth = srf.get_hypo(srf_file, depth=True)

    dbottom = []
    corners = np.zeros((len(planes), 4, 2))
    for i, p in enumerate(planes):
        # currently only support single dip dir value
        if dip_dir is not None:
            dip_deg = dip_dir
        else:
            dip_deg = p["strike"] + 90
        # projected fault width (along dip direction)
        pwid = p["width"] * math.cos(math.radians(p["dip"]))
        corners[i, 0] = geo.ll_shift(
            p["centre"][1], p["centre"][0], p["length"] / 2.0, p["strike"] + 180
        )[::-1]
        corners[i, 1] = geo.ll_shift(
            p["centre"][1], p["centre"][0], p["length"] / 2.0, p["strike"]
        )[::-1]
        corners[i, 2] = geo.ll_shift(corners[i, 1, 1], corners[i, 1, 0], pwid, dip_deg)[
            ::-1
        ]
        corners[i, 3] = geo.ll_shift(corners[i, 0, 1], corners[i, 0, 0], pwid, dip_deg)[
            ::-1
        ]
        dbottom.append(p["dtop"] + p["width"] * math.sin(math.radians(p["dip"])))

    if file_name is None:
        file_name = os.path.splitext(srf_file)[0]
    file_name = "{}.info".format(file_name)
    logger.debug("Saving info file to {}".format(file_name))
    with h5open(file_name, "w") as h:
        a = h.attrs
        # only taken from given parameters
        a["type"] = srf_type
        a["dt"] = dt
        a["rake"] = rake
        a["mag"] = mag
        # srf header data
        for k in planes[0].keys():
            a[k] = [p[k] for p in planes]
        # point source has 1 vs/rho, others are taken from vm
        if srf_type == 1:
            a["vs"] = vs
            a["rho"] = rho
            a["hlon"] = lon
            a["hlat"] = lat
            a["hdepth"] = centroid_depth
        else:
            a["vm"] = np.string_(os.path.basename(vm))
            a["hlon"] = hlon
            a["hlat"] = hlat
            a["hdepth"] = hdepth
            a["shyp0"] = shypo
            a["dhyp0"] = dhypo
        if mwsr is not None:
            a["mwsr"] = np.string_(mwsr)
        if tect_type is not None:
            a["tect_type"] = tect_type
        # derived parameters
        a["corners"] = corners
        a["dbottom"] = dbottom


def CreateSRF_ps(
    lat,
    lon,
    depth,
    mw,
    mom,
    strike,
    rake,
    dip,
    dt=0.005,
    prefix="source",
    stoch=None,
    vs=3.20,
    rho=2.44,
    target_area_km=None,
    target_slip_cm=None,
    stype="cos",
    rise_time=0.5,
    init_time=0.0,
    silent=False,
    logger: Logger = qclogging.get_basic_logger(),
):
    """
    Must specify either magnitude or moment (mw, mom).
    vs: Vs at hypocentre
    rho: density at hypocentre
    stype: source time function
    rise_time: sampling step
    init_time: time before rupture?
    """
    ###
    ### generate optional arguments
    ###
    # moment from magnitude
    if mom <= 0:
        mom = mag2mom(mw)
        logger.debug(
            "Determining moment from magnitude. Magnitude: {}. Moment: {}.".format(
                mw, mom
            )
        )
    # size (dd) and slip
    if target_area_km is not None:
        dd = math.sqrt(target_area_km)
        slip = (mom * 1.0e-20) / (target_area_km * vs * vs * rho)
        logger.debug("Determining slip from target_area_km. Slip: {}".format(slip))
    elif target_slip_cm is not None:
        dd = math.sqrt(mom * 1.0e-20) / (target_slip_cm * vs * vs * rho)
        slip = target_slip_cm
        logger.debug("Determining slip from target_slip_cm. Slip: {}".format(slip))
    else:
        aa = math.exp(2.0 * math.log(mom) / 3.0 - 14.7 * math.log(10.0))
        dd = math.sqrt(aa)
        slip = (mom * 1.0e-20) / (aa * vs * vs * rho)
        logger.debug("Determining slip from moment. Slip: {}".format(slip))

    logger.log(qclogging.logging.DEBUG * (1 + silent), "FLEN/FWID: {}".format(dd))

    ###
    ### file names
    ###
    if prefix[-1] == "_":
        prefix = "%s_%s" % (prefix, ("m%f" % (mw)).replace(".", "pt"))
    gsf_file = "%s.gsf" % (prefix)
    srf_file = "%s.srf" % (prefix)
    mkdir_p(os.path.dirname(srf_file), logger=logger)
    qclogging.remove_buffer_handler(logger)

    ###
    ### create GSF
    ###
    logger.debug("Creating gsf file. Save location: {}".format(gsf_file))
    with open(gsf_file, "w") as gsfp:
        gsfp.write("# nstk= 1 ndip= 1\n")
        gsfp.write("# flen= %10.4f fwid= %10.4f\n" % (dd, dd))
        gsfp.write(
            "# LON  LAT  DEP(km)  SUB_DX  SUB_DY  LOC_STK  LOC_DIP  LOC_RAKE  SLIP(cm)  INIT_TIME  SEG_NO\n"
        )
        gsfp.write("1\n")
        gsfp.write(
            "%11.5f %11.5f %8.4f %8.4f %8.4f %6.1f %6.1f %6.1f %8.2f %8.3f %3d\n"
            % (lon, lat, depth, dd, dd, strike, dip, rake, slip, init_time, 0)
        )

    ###
    ### create SRF
    ###
    if silent:
        stderr = PIPE
    else:
        stderr = None
    commands = [
        binary_version.get_unversioned_bin(GENERICSLIP2SRF),
        "infile=%s" % (gsf_file),
        "outfile=%s" % (srf_file),
        "outbin=0",
        "stype=%s" % (stype),
        "dt=%f" % (dt),
        "plane_header=1",
        "risetime=%f" % (rise_time),
        "risetimefac=1.0",
        "risetimedep=0.0",
    ]
    logger.debug('Calling slip2srf with command: "{}"'.format(" ".join(commands)))
    call(commands, stderr=stderr)

    ###
    ### save STOCH
    ###
    if stoch is not None:
        stoch_file = "%s/%s.stoch" % (stoch, os.path.basename(prefix))
        gen_stoch(stoch_file, srf_file, silent=silent, logger=logger)
    else:
        logger.debug("Not making stoch file")

    ###
    ### save INFO
    ###
    gen_meta(
        srf_file,
        1,
        mw,
        strike,
        rake,
        dip,
        dt,
        lon=lon,
        lat=lat,
        vs=vs,
        rho=rho,
        centroid_depth=depth,
        logger=logger,
    )

    # location of resulting SRF file
    return srf_file


def create_srf_psff(
    lat,
    lon,
    mw,
    strike,
    rake,
    dip,
    depth,
    dt,
    prefix,
    seed=None,
    flen=None,
    dlen=None,
    fwid=None,
    dwid=None,
    dtop=None,
    shypo=None,
    dhypo=None,
    stoch=None,
    mwsr=None,
    corners_file="cnrs.txt",
    genslip_version="3.3",
    rvfrac=None,
    rough=None,
    slip_cov=None,
    tect_type=None,
    silent=False,
    logger: Logger = qclogging.get_basic_logger(),
):
    """
    Create a Finite Fault SRF.
    Calculates flen, dlen... if not supplied given depth and mwsr are keywords.
    NOTE: depth is focal mech depth and only used when calculating flen etc...
    """

    seed = load_seed(prefix, seed, logger)

    srf_type = 2
    all_none = all(v is None for v in (flen, dlen, fwid, dwid, dtop, shypo, dhypo))
    any_none = any(v is None for v in (flen, dlen, fwid, dwid, dtop, shypo, dhypo))
    if all_none:
        (
            flen,
            dlen,
            fwid,
            dwid,
            dtop,
            lat,
            lon,
            shypo,
            dhypo,
        ) = focal_mechanism_2_finite_fault(
            lat, lon, depth, mw, strike, rake, dip, mwsr
        )[
            3:
        ]
    elif any_none:
        message = "If any of (flen, dlen, fwid, dwid, dtop, shypo, dhypo) are given, the rest must be given. Got: {}".format(
            (flen, dlen, fwid, dwid, dtop, shypo, dhypo)
        )
        logger.log(qclogging.NOPRINTCRITICAL, message)
        raise ValueError(
            "If any of (flen, dlen, fwid, dwid, dtop, shypo, dhypo) are given, the rest must be given. Got: {}".format(
                (flen, dlen, fwid, dwid, dtop, shypo, dhypo)
            )
        )

    # write corners file
    logger.debug("Getting corners")
    corners = get_corners(lat, lon, flen, fwid, dip, strike)
    hypocentre = get_hypocentre(lat, lon, flen, fwid, shypo, dhypo, strike, dip)
    logger.debug("Saving corners")
    write_corners(corners_file, hypocentre, corners)

    nx = get_nx(flen, dlen)
    ny = get_ny(fwid, dwid)
    if prefix[-1] == "_":
        prefix = "{}{}".format(prefix, get_fileroot(mw, flen, fwid, seed))
    gsf_file = "{}.gsf".format(prefix)
    srf_file = "{}.srf".format(prefix)
    out_dir = os.path.dirname(srf_file)
    mkdir_p(out_dir, logger=logger)

    gen_gsf(
        gsf_file, lon, lat, dtop, strike, dip, rake, flen, fwid, nx, ny, logger=logger
    )
    gen_srf(
        srf_file,
        gsf_file,
        mw,
        dt,
        nx,
        ny,
        seed,
        shypo,
        dhypo,
        genslip_version=genslip_version,
        rvfrac=rvfrac,
        slip_cov=slip_cov,
        rough=rough,
        logger=logger,
    )

    if stoch is not None:
        stoch_file = "%s/%s.stoch" % (stoch, os.path.basename(prefix))
        gen_stoch(
            stoch_file, srf_file, single_segment=True, silent=silent, logger=logger
        )

    # save INFO
    gen_meta(
        srf_file,
        srf_type,
        mw,
        strike,
        rake,
        dip,
        dt,
        lon=lon,
        lat=lat,
        centroid_depth=depth,
        mwsr=mwsr,
        shypo=shypo + 0.5 * flen,
        dhypo=dhypo,
        vm=srf_config.VELOCITY_MODEL,
        logger=logger,
    )

    # location of resulting SRF
    return srf_file


def load_seed(prefix, seed=None, logger: Logger = qclogging.get_basic_logger()):
    """If the seed is not None, pass it back, otherwise check for a seed file and load it if present, otherwise create a new seed and save it to a seed file"""
    seed_file = "{}.SEED".format(prefix)
    os.makedirs(os.path.dirname(seed_file), exist_ok=True)
    if seed is None:
        if os.path.isfile(seed_file):
            try:
                with open(seed_file) as sf:
                    seed = int(sf.readline())
            except IOError:
                message = "Unable to read seed from seed file {}. Please remove this before restarting".format(
                    seed_file
                )
                logger.log(qclogging.NOPRINTCRITICAL, message)
                raise IOError(message)
            else:
                logger.debug("Loaded seed from seed file, seed is: {}".format(seed))
        else:
            seed = get_seed()
            with open(seed_file, "w") as sf:
                sf.write("{}".format(seed))
            logger.debug("SEED: {}".format(seed))
    else:
        with open(seed_file, "w") as sf:
            sf.write("{}".format(seed))
    return seed


def CreateSRF_ff(
    lat,
    lon,
    mw,
    strike,
    rake,
    dip,
    dt,
    prefix0,
    seed,
    flen,
    dlen,
    fwid,
    dwid,
    dtop,
    shypo,
    dhypo,
    stoch=None,
    depth=None,
    corners=True,
    corners_file="cnrs.txt",
    genslip_version="3.3",
    rvfrac=None,
    rough=None,
    slip_cov=None,
    tect_type=None,
):
    """
    Create a Finite Fault SRF.
    Calculates flen, dlen... if not supplied given depth and mwsr are keywords.
    NOTE: depth is focal mech depth and only used when calculating flen etc...
    """

    # do not change input variables
    prefix = prefix0

    # only given point source parameters? calculate rest using scaling relation
    srf_type = 3

    # write corners file
    corners = get_corners(lat, lon, flen, fwid, dip, strike)
    hypocentre = get_hypocentre(lat, lon, flen, fwid, shypo, dhypo, strike, dip)
    write_corners(corners_file, hypocentre, corners)

    nx = get_nx(flen, dlen)
    ny = get_ny(fwid, dwid)
    if prefix[-1] == "_":
        prefix = "%s%s" % (prefix, get_fileroot(mw, flen, fwid, seed))
    gsf_file = "%s.gsf" % (prefix)
    srf_file = "%s.srf" % (prefix)
    out_dir = os.path.dirname(srf_file)
    mkdir_p(out_dir)

    gen_gsf(gsf_file, lon, lat, dtop, strike, dip, rake, flen, fwid, nx, ny)
    gen_srf(
        srf_file,
        gsf_file,
        mw,
        dt,
        nx,
        ny,
        seed,
        shypo,
        dhypo,
        genslip_version=genslip_version,
        rvfrac=rvfrac,
        slip_cov=slip_cov,
        rough=rough,
    )
    if stoch is not None:
        stoch_file = "%s/%s.stoch" % (stoch, os.path.basename(prefix))
        gen_stoch(stoch_file, srf_file, single_segment=True)

    gen_meta(
        srf_file,
        srf_type,
        mw,
        strike,
        rake,
        dip,
        dt,
        shypo=shypo + 0.5 * flen,
        dhypo=dhypo,
        tect_type=tect_type,
        vm=srf_config.VELOCITY_MODEL,
    )

    # location of resulting SRF
    return srf_file


def CreateSRF_multi(
    nseg,
    seg_delay,
    mag0,
    mom0,
    rvfac_seg,
    gwid,
    rup_delay,
    flen,
    dlen,
    fwid,
    dwid,
    dtop,
    stk,
    rak,
    dip,
    elon,
    elat,
    shypo,
    dhypo,
    dt,
    seed,
    prefix0,
    cases,
    genslip_version="3.3",
    rvfrac=None,
    rough=None,
    slip_cov=None,
    stoch=None,
    dip_dir=None,
    silent=False,
    velocity_model=None,
    tect_type=None,
    logger: Logger = qclogging.get_basic_logger(),
):
    if (
        utils.compare_versions(genslip_version, "5.4.2") < 0
        and tect_type == "SUBDUCTION_INTERFACE"
    ):
        raise RuntimeError(
            "Subduction interface faults are only available for version 5.4.2 and above"
        )

    # do not change any pointers
    mag = list(mag0)
    mom = list(mom0)
    prefix = prefix0

    if velocity_model is None:
        logger.debug(
            "No velocity model explicitly passed in, using {}".format(
                srf_config.VELOCITY_MODEL
            )
        )
        velocity_model = srf_config.VELOCITY_MODEL

    genslip_bin = binary_version.get_genslip_bin(genslip_version)
    if int(genslip_version[0]) < 5:
        logger.debug(
            "Using genslip version {}. Using nx, ny and rup_delay".format(
                genslip_version
            )
        )
        xstk = "nx"
        ydip = "ny"
        rup_name = "rup_delay"
    else:
        logger.debug(
            "Using genslip version {}. Using nstk, ndip and rupture_delay".format(
                genslip_version
            )
        )
        xstk = "nstk"
        ydip = "ndip"
        rup_name = "rupture_delay"
    out_dir = os.path.dirname(prefix)
    mkdir_p(out_dir, logger=logger)

    casefiles = []
    for c, case in enumerate(cases):
        logger.debug("Generating realisation {}".format(c))

        if mom[c] <= 0:
            mom[c] = mag2mom(mag[c])
            logger.debug(
                "Given moment is negative, determining from magnitude. Magnitude: {}. Moment: {}.".format(
                    mag[c], mom[c]
                )
            )
        else:
            mag[c] = mom2mag(mom[c])
            logger.debug(
                "Determining magnitude from moment. Moment: {}. Magnitude: {}.".format(
                    mom[c], mag[c]
                )
            )

        nx = list(map(int, [get_nx(flen[c][f], dlen[c][f]) for f in range(nseg[c])]))
        ny = list(map(int, [get_ny(fwid[c][f], dwid[c][f]) for f in range(nseg[c])]))
        nx_tot = sum(nx)
        flen_tot = sum(flen[c])
        # hypocentre is given based on the first segment
        # needs to be relative to full length instead of first segment
        shyp_tot = shypo[c][0] + 0.5 * flen[c][0] - 0.5 * flen_tot

        xseg = "-1"
        if int(nseg[c] > 1):
            logger.debug("Multiple segments detected. Generating xseg argument")
            xseg = []
            sbound = 0.0
            for g in range(nseg[c]):
                sbound += flen[c][g]
                xseg.append(sbound - 0.5 * flen_tot)
            xseg = ",".join(map(str, xseg))

        case_root = "{}_{}".format(prefix.rstrip("_"), case)
        gsf_file = "{}.gsf".format(case_root)
        srf_file = "{}.srf".format(case_root)
        fsg_file = "{}_seg.in".format(case_root)
        casefiles.append(srf_file)

        logger.debug("Saving segments file to {}".format(fsg_file))
        with open(fsg_file, "w") as fs:
            fs.write("{}\n".format(nseg[c]))
            for f in range(nseg[c]):
                fs.write(
                    "{:f} {:f} {:f} {:.4f} {:.4f} {:.4f} {:.4f} {:.4f} {:d} {:d}\n".format(
                        elon[c][f],
                        elat[c][f],
                        dtop[c][f],
                        stk[c][f],
                        dip[c][f],
                        rak[c][f],
                        flen[c][f],
                        fwid[c][f],
                        nx[f],
                        ny[f],
                    )
                )
        # create GSF file
        cmd = [
            binary_version.get_unversioned_bin(FAULTSEG2GSFDIPDIR),
            "read_slip_vals=0",
            "infile={}".format(fsg_file),
            "outfile={}".format(gsf_file),
        ]
        if dip_dir is not None:
            cmd.append("dipdir={}".format(dip_dir))
        logger.info(
            "Calling fault_seg2gsf_dipdir with command {}".format(" ".join(cmd))
        )
        call(cmd)
        os.remove(fsg_file)
        logger.debug("Removed segments file")

        with open(srf_file, "w") as srfp:
            cmd = [
                genslip_bin,
                "read_erf=0",
                "write_srf=1",
                "seg_delay={}".format(seg_delay[c]),
                "read_gsf=1",
                "write_gsf=1",
                "infile={}".format(gsf_file),
                "nseg={}".format(nseg[c]),
                "nseg_bounds={}".format(nseg[c] - 1),
                "xseg={}".format(xseg),
                "rvfac_seg={}".format(rvfac_seg[c]),
                "gwid={}".format(gwid[c]),
                "mag={}".format(mag[c]),
                "{}={}".format(xstk, nx_tot),
                "{}={}".format(ydip, ny[0]),
                "ns=1",
                "nh=1",
                "seed={}".format(seed),
                "velfile={}".format(velocity_model),
                "shypo={}".format(shyp_tot),
                "dhypo={}".format(dhypo[c][0]),
                "dt={}".format(dt),
                "plane_header=1",
                "side_taper=0.02",
                "bot_taper=0.02",
                "top_taper=0.0",
                "{}={}".format(rup_name, rup_delay[c]),
                "srf_version=1.0",
            ]
            if tect_type == "SUBDUCTION_INTERFACE":
                cmd.append("kmodel=-1")
                cmd.append("xmag_exp=0.5")
                cmd.append("ymag_exp=0.5")
                cmd.append("kx_corner=2.5482")
                cmd.append("ky_corner=2.3882")
                cmd.append("tsfac_slope=-0.5")
                cmd.append("tsfac_bzero=-0.1")
                cmd.append("risetime_coef=1.95")
            if rvfrac is not None:
                cmd.append("rvfrac={}".format(rvfrac))
            if rough is not None:
                cmd.append("alpha_rough={}".format(rough))
            if slip_cov is not None:
                cmd.append("slip_sigma={}".format(slip_cov))
            logger.debug("Calling genslip with command {}".format(cmd))
            if silent:
                with open("/dev/null", "a") as sink:
                    call(cmd, stdout=srfp, stderr=sink)
            else:
                call(cmd, stdout=srfp)
        os.remove(gsf_file)
        logger.debug("Removed gsf file")
        # print leonard Mw from A (SCR)
        if not silent:
            print("Leonard 2014 Mw: %s" % (leonard(rak[c][f], fwid[c][f] * flen[c][f])))

    # joined filename
    if prefix[-1] == "_":
        prefix = "{}s{}".format(prefix, seed)
    joined_srf = "{}.srf".format(prefix)
    # joined case files stored in separate file
    copyfile(casefiles[0], joined_srf)
    # join rest of cases into the first
    for i in range(len(cases) - 1):
        srf_join(joined_srf, casefiles[i + 1], joined_srf)
    # remove casefiles
    for casefile in casefiles:
        os.remove(casefile)
    if stoch is not None:
        single_segment = False
        if nseg == 1:
            single_segment = True
        stoch_file = os.path.join(stoch, "{}.stoch".format(os.path.basename(prefix)))
        gen_stoch(
            stoch_file,
            joined_srf,
            silent=silent,
            single_segment=single_segment,
            logger=logger,
        )
    # save INFO
    gen_meta(
        joined_srf,
        4,
        mag[0],
        stk,
        np.asarray(rak),
        dip,
        dt,
        vm=velocity_model,
        dip_dir=dip_dir,
        shypo=[s[0] + 0.5 * flen[c][0] for s in shypo],
        dhypo=[d[0] for d in dhypo],
        tect_type=tect_type,
        logger=logger,
    )

    # path to resulting SRF
    return joined_srf


if __name__ == "__main__":
    logger = qclogging.get_logger("createSRF")
    qclogging.add_general_file_handler(logger, "createSRF_log.txt")
    try:
        from setSrfParams import *
    except ImportError:
        logger.error("setSrfParams.py not found.")
        exit(1)
    except:
        logger.error("Error: setSrfParams.py has issues.")
        print(sys.exc_info()[0])
        raise

    # incomplete defaults compatibility
    try:
        RVFRAC
    except NameError:
        RVFRAC = None
    try:
        ROUGH
    except NameError:
        ROUGH = None
    try:
        SLIP_COV
    except NameError:
        SLIP_COV = None
    try:
        STOCH
    except NameError:
        STOCH = None

    if TYPE == 1:
        # point source to point source srf
        srf = CreateSRF_ps(
            LAT,
            LON,
            DEPTH,
            MAG,
            MOM,
            STK,
            RAK,
            DIP,
            DT,
            PREFIX,
            stoch=STOCH,
            logger=logger,
        )
    elif TYPE == 2:
        # point source to finite fault srf
        srf = create_srf_psff(
            LAT,
            LON,
            MAG,
            STK,
            RAK,
            DIP,
            DEPTH,
            DT,
            PREFIX,
            SEED,
            mwsr=MWSR,
            stoch=STOCH,
            genslip_version=GENSLIP,
            rvfrac=RVFRAC,
            slip_cov=SLIP_COV,
            rough=ROUGH,
            logger=logger,
        )
    elif TYPE == 3:
        # finite fault descriptor to finite fault srf
        srf = CreateSRF_ff(
            LAT,
            LON,
            MAG,
            STK,
            RAK,
            DIP,
            DT,
            PREFIX,
            SEED,
            FLEN,
            DLEN,
            FWID,
            DWID,
            DTOP,
            SHYPO,
            DHYPO,
            stoch=STOCH,
            corners=True,
            genslip_version=GENSLIP,
            rvfrac=RVFRAC,
            slip_cov=SLIP_COV,
            rough=ROUGH,
            logger=logger,
        )
    elif TYPE == 4:
        # multi segment finite fault srf
        srf = CreateSRF_multi(
            M_NSEG,
            M_SEG_DELAY,
            M_MAG,
            M_MOM,
            M_RVFAC_SEG,
            M_GWID,
            M_RUP_DELAY,
            M_FLEN,
            M_DLEN,
            M_FWID,
            M_DWID,
            M_DTOP,
            M_STK,
            M_RAK,
            M_DIP,
            M_ELON,
            M_ELAT,
            M_SHYPO,
            M_DHYPO,
            DT,
            SEED,
            PREFIX,
            CASES,
            genslip_version=GENSLIP,
            rvfrac=RVFRAC,
            slip_cov=SLIP_COV,
            stoch=STOCH,
            rough=ROUGH,
            logger=logger,
        )
    else:
        print("Bad type of SRF generation specified. Check parameter file.")
        exit(1)

    # run SRF plots
    if len(sys.argv) > 1 and sys.argv[1] == "noplot":
        exit(0)

    if TYPE == 1:
        print("Point source plotting not yet implemented.")
        exit(0)

    for script in ["plot_srf_square.py", "plot_srf_map.py"]:
        path_tester = Popen(["which", script], stdout=PIPE)
        script_path = path_tester.communicate()[0].rstrip()
        path_tester.wait()
        if not os.path.exists(script_path):
            print("Plotting script %s is not available in PATH!" % (script))
            exit(1)

    print("Plotting SRF as square plot...")
    call(["plot_srf_square.py", srf])
    print("Plotting SRF as map plot...")
    call(["plot_srf_map.py", srf])
