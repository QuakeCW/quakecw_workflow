#!/usr/bin/env python
"""
Combines low frequency and high frequency seismograms.
"""

from argparse import ArgumentParser
import os
import logging
import numpy as np

from qcore.siteamp_models import nt2n, cb_amp, ba18_amp, init_ba18
from qcore import timeseries, utils
from qcore.constants import VM_PARAMS_FILE_NAME, Components, PLATFORM_CONFIG
from site_response_BB import site_response
from platform_config_shim import platform_config

if __name__ == "__main__":
    from mpi4py import MPI
    from qcore import MPIFileHandler

N_COMPONENTS = 3

ampdeamp = timeseries.ampdeamp
bwfilter = timeseries.bwfilter
HEAD_SIZE = timeseries.BBSeis.HEAD_SIZE
HEAD_STAT = timeseries.BBSeis.HEAD_STAT
FLOAT_SIZE = 0x4
N_COMP = 3


def args_parser(cmd=None):
    """
    CMD is a list of strings to parse
    While, not None, cmd will be used to parse
    if cmd == None, default behavior sys.argv[1:] will be used
    """
    parser = ArgumentParser()
    arg = parser.add_argument
    arg("lf_dir", help="LF OutBin folder containing SEIS files")
    arg("lf_vm", help="LF VM folder containing velocity model")
    arg("hf_file", help="HF file path")
    arg("vsite_file", help="Vs30 station file")
    arg("out_file", help="BB output file path")
    arg("--flo", help="low/high frequency cutoff", type=float)
    arg("--fmin", help="fmin for site amplification", type=float, default=0.2)
    arg("--fmidbot", help="fmidbot for site amplification", type=float, default=0.5)
    arg("--lfvsref", help="Override LF Vs30 reference value (m/s)", type=float)
    arg("--dt", help="timestep (seconds)", type=float)
    arg(
        "--no-lf-amp",
        help="Disable site amplification for LF component",
        action="store_true",
    )
    arg(
        "--site-amp",
        help="Choose the site-amp model to be used",
        default="CB14",
        choices=["CB08", "CB14", "BA18"],
    )
    arg(
        "--site_response_dir",
        help="The directory with site response yaml files for OpenSees amplification. Without an argument uses the default.",
        default=False,
        const=platform_config[
            PLATFORM_CONFIG.DEFAULT_SITE_RESPONSE_DIR.name
        ],
        nargs="?",
    )

    args = parser.parse_args(cmd)
    return args


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    master = 0
    is_master = not rank

    logger = logging.getLogger("rank_%i" % comm.rank)
    logger.setLevel(logging.DEBUG)

    # collect required arguments
    args = None
    if is_master:
        try:
            args = args_parser()
        except SystemExit as e:
            # invalid arguments or -h
            print("arg parse error occured:", e)
            comm.Abort()

    args = comm.bcast(args, root=master)

    mh = MPIFileHandler.MPIFileHandler(
        os.path.join(os.path.dirname(args.out_file), "BB.log")
    )
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    mh.setFormatter(formatter)
    logger.addHandler(mh)

    site_amp_version = None
    amp_function = None
    if args.site_amp == "CB14" or args.site_amp == "CB08":
        amp_function = cb_amp
        if args.site_amp == "CB08":
            site_amp_version = "2008"
        else:
            site_amp_version = "2014"
    elif args.site_amp == "BA18":
        init_ba18()
        amp_function = ba18_amp

    if args.no_lf_amp:

        def ampdeamp_lf(series, *x, **y):
            return series

        def lf_amp_function(*x, **y):
            pass

    else:
        ampdeamp_lf = ampdeamp
        lf_amp_function = amp_function

    # load data stores
    lf = timeseries.LFSeis(args.lf_dir)
    hf = timeseries.HFSeis(args.hf_file)

    # compatibility validation
    # abort if behaviour is undefined
    if is_master:
        logger.debug("=" * 50)
        if not lf.nstat == hf.nstat:
            logger.error("LF nstat != HF nstat. {} vs {}".format(lf.nstat, hf.nstat))
            comm.Abort()
        if set(lf.stations.name) != set(hf.stations.name):
            logger.error("LF and HF were run with different station files")
            comm.Abort()
        if not np.isclose(
            lf.dt * lf.nt + lf.start_sec, hf.dt * hf.nt, atol=min(lf.dt, hf.dt)
        ):
            logger.error(
                "LF duration != HF duration. {} vs {}".format(
                    lf.dt * lf.nt + lf.start_sec, hf.dt * hf.nt
                )
            )
            comm.Abort()

    # load metadata
    if args.dt is None:
        bb_dt = min(lf.dt, hf.dt)
    else:
        bb_dt = args.dt

    # As LF has a start time offset it is necessary to pad the start of HF by the same number of timesteps
    # Similar code to account for an end time difference is also present
    # allowing for HF and LF to have separate start times and durations
    bb_start_sec = min(lf.start_sec, hf.start_sec)
    lf_start_sec_offset = max(lf.start_sec - hf.start_sec, 0)
    hf_start_sec_offset = max(hf.start_sec - lf.start_sec, 0)

    lf_start_padding = int(round(lf_start_sec_offset / bb_dt))  # Uses np.round
    hf_start_padding = int(round(hf_start_sec_offset / bb_dt))

    lf_end_padding = int(
        round(
            max(
                hf.duration + hf_start_sec_offset - (lf.duration + lf_start_sec_offset),
                0,
            )
            / bb_dt
        )
    )
    hf_end_padding = int(
        round(
            max(
                lf.duration + lf_start_sec_offset - (hf.duration + hf_start_sec_offset),
                0,
            )
            / bb_dt
        )
    )

    assert (
        lf_start_padding + round(lf.duration / bb_dt) + lf_end_padding
        == hf_start_padding + round(hf.duration / bb_dt) + hf_end_padding
    )

    bb_nt = int(lf_start_padding + round(lf.duration / bb_dt) + lf_end_padding)
    n2 = nt2n(bb_nt)

    lf_start_padding_ts = np.zeros(lf_start_padding)
    hf_start_padding_ts = np.zeros(hf_start_padding)
    lf_end_padding_ts = np.zeros(lf_end_padding)
    hf_end_padding_ts = np.zeros(hf_end_padding)

    head_total = HEAD_SIZE + lf.stations.size * HEAD_STAT
    file_size = head_total + lf.stations.size * bb_nt * N_COMP * FLOAT_SIZE
    if args.flo is None:
        # min_vs / (5.0 * hh)
        args.flo = 0.5 / (5.0 * lf.hh)

    if is_master:
        # Logging each argument
        for key in vars(args):
            logger.debug("{} : {}".format(key, getattr(args, key)))

    comm.Barrier()  # prevent other processes from messing log file until master is done with logging above
    # load vs30ref
    if args.lfvsref is None:
        # vs30ref from velocity model
        vm_conf = utils.load_yaml(os.path.join(args.lf_vm, VM_PARAMS_FILE_NAME))
        lfvs30refs = (
            np.memmap(
                "%s/vs3dfile.s" % (args.lf_vm),
                dtype="<f4",
                shape=(vm_conf["ny"], vm_conf["nz"], vm_conf["nx"]),
                mode="r",
            )[lf.stations.y, 0, lf.stations.x]
            * 1000.0
        )
        if is_master:
            logger.debug("vs30ref from velocity model.")
    else:
        # fixed vs30ref
        lfvs30refs = np.ones(lf.stations.size, dtype=np.float32) * args.lfvsref
        if is_master:
            logger.debug("fixed vs30ref.")

    # load vs30
    try:
        # has to be a numpy array of np.float32 as written directly to binary
        vs30s = np.vectorize(
            dict(
                np.loadtxt(
                    args.vsite_file,
                    dtype=[("name", "|U8"), ("vs30", "f4")],
                    comments=("#", "%"),
                )
            ).get
        )(lf.stations.name)
        assert not np.isnan(vs30s).any()
    except AssertionError:
        if is_master:
            logger.error("vsite file is missing stations.")
            comm.Abort()
    else:
        if is_master:
            logger.debug("vs30 loaded successfully.")

    # initialise output with general metadata
    def initialise(check_only=False):
        logger.debug("Initialising.")
        with open(args.out_file, mode="rb" if check_only else "w+b") as out:
            # int/bool parameters
            i = np.array([lf.stations.size, bb_nt], dtype="i4")
            # float parameters
            f = np.array([bb_nt * bb_dt, bb_dt, bb_start_sec], dtype="f4")
            # string parameters
            s = np.array([args.lf_dir, args.lf_vm, args.hf_file], dtype="|S256")
            # station metadata
            bb_stations = np.rec.array(
                np.zeros(
                    lf.nstat,
                    dtype={
                        "names": [
                            "lon",
                            "lat",
                            "name",
                            "x",
                            "y",
                            "z",
                            "e_dist",
                            "hf_vs_ref",
                            "lf_vs_ref",
                        ],
                        "formats": [
                            "f4",
                            "f4",
                            "|S8",
                            "i4",
                            "i4",
                            "i4",
                            "f4",
                            "f4",
                            "f4",
                        ],
                        "itemsize": HEAD_STAT,
                    },
                )
            )
            # copy most from LF
            for col in bb_stations.dtype.names[:-3]:
                bb_stations[col] = lf.stations[col]
            # add e_dist and hf_vs_ref from HF
            # assuming same order, true if run with same station file, asserted above
            bb_stations.e_dist = hf.stations.e_dist
            bb_stations.hf_vs_ref = hf.stations.vs
            # lf_vs_ref from velocity model
            bb_stations.lf_vs_ref = lfvs30refs

            # verify or write
            if check_only:
                for a in [i, f, s, bb_stations]:
                    if a is bb_stations:
                        out.seek(HEAD_SIZE)
                    assert np.all(np.fromfile(out, dtype=a.dtype, count=a.size) == a)
            else:
                i.tofile(out)
                f.tofile(out)
                s.tofile(out)
                out.seek(HEAD_SIZE)
                bb_stations.tofile(out)
                # fill space
                out.seek(file_size - FLOAT_SIZE)
                np.float32().tofile(out)

    def unfinished():
        try:
            with open(args.out_file, "rb") as bbf:
                bbf.seek(HEAD_SIZE)
                # checkpoints are vsite written to file
                # assume continuing machine is the same endian
                ckpoints = (
                    np.fromfile(
                        bbf,
                        count=lf.stations.size,
                        dtype={
                            "names": ["vsite"],
                            "formats": ["f4"],
                            "offsets": [40],
                            "itemsize": HEAD_STAT,
                        },
                    )["vsite"]
                    > 0
                )
        except IOError:
            # file not created yet
            return
        if os.stat(args.out_file).st_size != file_size or len(ckpoints) == 0:
            # file size is incorrect (probably different simulation)
            return
        if np.min(ckpoints):
            try:
                logger.debug("Checkpoints found.")
                initialise(check_only=True)
                logger.error("BB Simulation already completed.")
                comm.Abort()
            except AssertionError:
                return
        # seems ok to continue simulation
        return np.invert(ckpoints)

    station_mask = None
    if is_master:
        station_mask = unfinished()
        if station_mask is None or sum(station_mask) == lf.stations.size:
            logger.debug("No valid checkpoints found. Starting fresh simulation.")
            initialise()
            station_mask = np.ones(lf.stations.size, dtype=np.bool)
        else:
            try:
                initialise(check_only=True)
                logger.info(
                    "{} of {} stations completed. Resuming simulation.".format(
                        lf.stations.size - sum(station_mask), lf.stations.size
                    )
                )

            except AssertionError:
                logger.warning(
                    "Simulation parameters mismatch. Starting fresh simulation."
                )
                initialise()
                station_mask = np.ones(lf.stations.size, dtype=np.bool)
    station_mask = comm.bcast(station_mask, root=master)
    stations_todo = hf.stations[station_mask][rank::size]
    stations_todo_idx = np.arange(hf.stations.size)[station_mask][rank::size]

    # load container to write to
    bin_data = open(args.out_file, "r+b")
    bin_seek = head_total + stations_todo_idx * bb_nt * N_COMP * FLOAT_SIZE
    bin_seek_vsite = HEAD_SIZE + stations_todo_idx * HEAD_STAT + 40

    # work on station subset
    fmin = args.fmin
    fmidbot = args.fmidbot
    t0 = MPI.Wtime()
    bb_acc = np.empty((bb_nt, N_COMP), dtype="f4")
    for i, stat in enumerate(stations_todo):
        logger.debug(
            f"Working on {stat.name}, {100*i/len(stations_todo):.2f}% complete"
        )
        lf_acc = np.copy(lf.acc(stat.name, dt=bb_dt))
        hf_acc = np.copy(hf.acc(stat.name, dt=bb_dt))
        station_yaml = os.path.join(str(args.site_response_dir), f"{stat.name}.yaml")
        if args.site_response_dir and os.path.isfile(station_yaml):
            logger.debug(
                f"Station {stat.name} has a site specific file. Running OpenSees"
            )
            site_properties = site_response.SiteProp.from_file(station_yaml)
            for c in range(N_COMPONENTS):
                hf_filtered = bwfilter(
                    hf_acc[:, c],
                    bb_dt,
                    args.flo,
                    "highpass",
                )
                lf_filtered = bwfilter(
                    lf_acc[:, c],
                    bb_dt,
                    args.flo,
                    "lowpass",
                )
                hf_c = np.hstack((hf_start_padding_ts, hf_filtered, hf_end_padding_ts))
                lf_c = np.hstack((lf_start_padding_ts, lf_filtered, lf_end_padding_ts))
                bb_acc[:, c] = (
                    site_response.deconvolve_timeseries_and_run_site_response(
                        hf_c + lf_c,
                        Components(c),
                        site_properties,
                        dt=bb_dt,
                        logger=logger,
                    )
                    / 9.81
                )

        else:
            if args.site_response_dir:
                logger.debug(
                    f"Station {stat.name} does not have a site specific file. Running vs30 based amplification"
                )
            else:
                logger.debug(
                    f"Site specific response not being used. Running vs30 based amplification for {stat.name}"
                )
            pga = np.max(np.abs(hf_acc), axis=0) / 981.0
            # ideally remove loop # Could reduce to single components?
            for c in range(N_COMPONENTS):
                hf_amp_val = amp_function(
                    bb_dt,
                    n2,
                    stat.vs,
                    vs30s[stations_todo_idx[i]],
                    stat.vs,
                    pga[c],
                    fmin=fmin,
                    fmidbot=fmidbot,
                    version=site_amp_version,
                )
                lf_amp_val = lf_amp_function(
                    bb_dt,
                    n2,
                    lfvs30refs[stations_todo_idx[i]],
                    vs30s[stations_todo_idx[i]],
                    stat.vs,
                    pga[c],
                    fmin=fmin,
                    fmidbot=fmidbot,
                    version=site_amp_version,
                )
                hf_filtered = bwfilter(
                    ampdeamp(
                        hf_acc[:, c],
                        hf_amp_val,
                        amp=True,
                    ),
                    bb_dt,
                    args.flo,
                    "highpass",
                )
                lf_filtered = bwfilter(
                    ampdeamp_lf(
                        lf_acc[:, c],
                        lf_amp_val,
                        amp=True,
                    ),
                    bb_dt,
                    args.flo,
                    "lowpass",
                )
                hf_c = np.hstack((hf_start_padding_ts, hf_filtered, hf_end_padding_ts))
                lf_c = np.hstack((lf_start_padding_ts, lf_filtered, lf_end_padding_ts))
                if is_master and i == 0:
                    if len(hf_c) != len(lf_c):
                        logger.critical(
                            "padded hf and lf have different number of timesteps, aborting. "
                        )
                        comm.Abort()
                bb_acc[:, c] = (hf_c + lf_c) / 981.0

        bin_data.seek(bin_seek[i])
        bb_acc.tofile(bin_data)
        # write vsite as used for checkpointing
        bin_data.seek(bin_seek_vsite[i])
        vs30s[stations_todo_idx[i]].tofile(bin_data)
    bin_data.close()

    print("Process %03d of %03d finished (%.2fs)." % (rank, size, MPI.Wtime() - t0))
    logger.debug(
        "Process {} of {} completed {} stations ({:.2f}).".format(
            rank, size, len(stations_todo), MPI.Wtime() - t0
        )
    )
    comm.Barrier()  # all ranks wait here until rank 0 arrives to announce all completed
    if is_master:
        logger.debug("Simulation completed.")


if __name__ == "__main__":
    main()
