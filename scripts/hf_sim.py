#!/usr/bin/env python
"""
Simulates high frequency seismograms for stations.
"""
from argparse import ArgumentParser
import os
import random
from subprocess import Popen, PIPE
from tempfile import mkstemp

import numpy as np
import logging

from qcore import binary_version, constants, utils
from platform_config_shim import platform_config

if __name__ == "__main__":
    from qcore import MPIFileHandler
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    master = 0
    is_master = rank == master

    logger = logging.getLogger("rank_%i" % comm.rank)
    logger.setLevel(logging.DEBUG)

HEAD_SIZE = 0x0200
HEAD_STAT = 0x18
FLOAT_SIZE = 0x4
N_COMP = 3

# never changed / unknown function (line 6)
nbu = 4
ift = 0
flo = 0.02
fhi = 19.9
# for line 15
nl_skip = -99
vp_sig = 0.0
vsh_sig = 0.0
rho_sig = 0.0
qs_sig = 0.0
ic_flag = True
# seems to store details in {velocity_name}_{station_name}.1d if not '-1'
velocity_name = "-1"


def random_seed():
    return random.randrange(1_000_000, 9_999_999)


def args_parser(cmd=None):
    """
    CMD is a list of strings to parse
    While, not None, cmd will be used to parse
    if cmd == None, default behavior sys.argv[1:] will be used
    """

    parser = ArgumentParser()
    arg = parser.add_argument
    # HF IN, line 12
    arg("--slip", required=True, dest="stoch_file", help="rupture model")
    # HF IN, line 2
    arg("station_file", help="station file (lon, lat, name)")
    # HF IN, line 3
    arg("out_file", help="file path for HF output")
    # ARG 0
    arg(
        "--sim_bin",
        help="high frequency binary (modified for binary out)",
        default=None,
        type=os.path.abspath,
    )
    arg(
        "--version",
        help="binary version, similar to --sim_bin but not full path.",
        default="6.0.3",  # 5.4.5, 5.4.6, 6.0.3 with subversions .1 .2 .3 are supported
    )
    arg("--t-sec", help="high frequency output start time", type=float, default=0.0)
    # HF IN, line 1
    arg("--sdrop", help="stress drop average (bars)", type=float, default=50.0)
    # HF IN, line 4
    arg(
        "--rayset",
        help="ray types 1:direct 2:moho",
        nargs="+",
        type=int,
        default=[1, 2],
    )
    # HF IN, line 5
    arg(
        "--no-siteamp",
        help="disable BJ97 site amplification factors",
        action="store_true",
    )
    # HF IN, line 7
    arg(
        "--seed",
        help="random seed (0:randomised reproducible)",
        type=int,
        default=constants.HF_DEFAULT_SEED,
    )
    # HF IN, line 9
    arg("--duration", help="output length (seconds)", type=float, default=100.0)
    arg("--dt", help="timestep (seconds)", type=float, default=0.005)
    arg("--fmax", help="max sim frequency (Hz)", type=float, default=10)
    arg("--kappa", help="", type=float, default=0.045)
    arg("--qfexp", help="Q frequency exponent", type=float, default=0.6)
    # HF IN, line 10
    arg(
        "--rvfac",
        help="rupture velocity factor (rupture : Vs)",
        type=float,
        default=0.8,
    )
    arg("--rvfac_shal", help="rvfac shallow fault multiplier", type=float, default=0.7)
    arg("--rvfac_deep", help="rvfac deep fault multiplier", type=float, default=0.7)
    arg(
        "--czero",
        help="C0 coefficient, < -1 for binary default",
        type=float,
        default=2.1,
    )
    arg(
        "--calpha",
        help="Ca coefficient, < -1 for binary default",
        type=float,
        default=-99,
    )
    # HF IN, line 11
    arg("--mom", help="seismic moment, -1: use rupture model", type=float, default=-1.0)
    arg(
        "--rupv",
        help="rupture velocity, -1: use rupture model",
        type=float,
        default=-1.0,
    )
    # HF IN, line 13
    arg(
        "-m",
        "--hf_vel_mod_1d",
        help="path to velocity model (1D). ignored if --site_specific is set",
        default=os.path.join(
            platform_config[constants.PLATFORM_CONFIG.VELOCITY_MODEL_DIR.name],
            "Mod-1D/Cant1D_v2-midQ_leer.1d",
        ),
    )
    arg(
        "--site_specific",
        action="store_true",
        help="enable site-specific calculation",
        default=False,
    )
    arg(
        "-s",
        "--site_v1d_dir",
        help="dir containing site specific velocity models (1D). requires --site_specific",
    )
    # HF IN, line 14
    arg("--vs-moho", help="vs of moho layer, < 0 for 999.9", type=float, default=999.9)
    # HF IN, line 17
    arg("--fa_sig1", help="fourier amplitute uncertainty (1)", type=float, default=0.0)
    arg("--fa_sig2", help="fourier amplitude uncertainty (2)", type=float, default=0.0)
    arg("--rv_sig1", help="rupture velocity uncertainty", type=float, default=0.1)
    # HF IN, line 18
    arg(
        "--path_dur",
        help="""path duration model
        0:GP2010 formulation
        1:[DEFAULT] WUS modification trial/error
        2:ENA modification trial/error
        11:WUS formulation of BT2014, overpredicts for multiple rays
        12:ENA formulation of BT2015, overpredicts for multiple rays""",
        type=int,
        default=1,
    )
    arg(
        "--dpath_pert",
        help="""path duration perturbation
        Only to be used with versions greater than 5.4.5.4
        The path duration is multiplied by the base e exponential of the given value
        The default value of 0 results in no perturbation""",
        type=float,
        default=0.0,
    )

    arg(
        "--stress_param_adj",
        help="""stress parameter adjustment X Y Z
        X: Adjustment option 0 = off 1 = active tectonic, 2 = stable continent
        Y: Target magnitude (auto = -1 or specified mag.)
        Z: Fault area (auto = -1 or specified area in km^2)""",
        nargs=3,
        default=["1", "-1", "-1"],
    )

    args = parser.parse_args(cmd)

    return args


if __name__ == "__main__":
    args = None
    if is_master:
        try:
            args = args_parser()
        except SystemExit as e:
            print(e, flush=True)
            # invalid arguments or -h
            comm.Abort(1)

        if args.sim_bin is None:
            args.sim_bin = binary_version.get_hf_binmod(args.version)

        logger.debug("=" * 50)
        # random seed
        seed_file = os.path.join(os.path.dirname(args.out_file), "SEED")

        if os.path.isfile(seed_file):
            args.seed = np.loadtxt(seed_file, dtype="i", ndmin=1)[0]
            logger.debug("seed taken from file: {}".format(args.seed))
        elif args.seed == 0:
            args.seed = random_seed()
            np.savetxt(seed_file, np.array([args.seed], dtype=np.int32), fmt="%i")
            logger.debug("seed generated: {}".format(args.seed))
        else:
            logger.debug("seed from command line: {}".format(args.seed))
        assert args.seed >= 0  # don't like negative seed

        # Logging each argument
        for key in vars(args):
            logger.debug("{} : {}".format(key, getattr(args, key)))

    args = comm.bcast(args, root=master)

    mh = MPIFileHandler.MPIFileHandler(
        os.path.join(os.path.dirname(args.out_file), "HF.log")
    )
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    mh.setFormatter(formatter)
    logger.addHandler(mh)

    nt = int(round(args.duration / args.dt))
    stations = np.loadtxt(
        args.station_file,
        ndmin=1,
        dtype=[("lon", "f4"), ("lat", "f4"), ("name", "|S8")],
    )
    head_total = HEAD_SIZE + HEAD_STAT * stations.size
    block_size = nt * N_COMP * FLOAT_SIZE
    file_size = head_total + stations.size * block_size

    # initialise output with general metadata
    def initialise(check_only=False):
        with open(args.out_file, mode="rb" if check_only else "w+b") as out:
            # int/bool parameters, rayset must be fixed to length = 4
            fwrs = args.rayset + [0] * (4 - len(args.rayset))
            i4 = np.array(
                [
                    stations.size,
                    nt,
                    args.seed,
                    not args.no_siteamp,
                    args.path_dur,
                    len(args.rayset),
                    fwrs[0],
                    fwrs[1],
                    fwrs[2],
                    fwrs[3],
                    nbu,
                    ift,
                    nl_skip,
                    ic_flag,
                    args.seed >= 0,
                    args.site_specific is True,
                ],
                dtype="i4",
            )
            # float parameters
            f4 = np.array(
                [
                    args.duration,
                    args.dt,
                    args.t_sec,
                    args.sdrop,
                    args.kappa,
                    args.qfexp,
                    args.fmax,
                    flo,
                    fhi,
                    args.rvfac,
                    args.rvfac_shal,
                    args.rvfac_deep,
                    args.czero,
                    args.calpha,
                    args.mom,
                    args.rupv,
                    args.vs_moho,
                    vp_sig,
                    vsh_sig,
                    rho_sig,
                    qs_sig,
                    args.fa_sig1,
                    args.fa_sig2,
                    args.rv_sig1,
                ],
                dtype="f4",
            )
            # string parameters
            if args.site_specific is True:
                v1d = (
                    args.site_v1d_dir
                )  # dir only is ok. i4 above has last element to deduce actual VM file
            else:
                v1d = args.hf_vel_mod_1d
            s64 = np.array(
                list(map(os.path.basename, [args.stoch_file, v1d])), dtype="|S64"
            )
            # station metadata
            stat_head = np.zeros(
                stations.size,
                dtype={
                    "names": ["lon", "lat", "name"],
                    "formats": ["f4", "f4", "|S8"],
                    "itemsize": HEAD_STAT,
                },
            )
            for column in stat_head.dtype.names:
                stat_head[column] = stations[column]

            # verify or write
            if check_only:
                assert np.min(np.fromfile(out, dtype=i4.dtype, count=i4.size) == i4)
                assert np.min(np.fromfile(out, dtype=f4.dtype, count=f4.size) == f4)
                assert np.min(np.fromfile(out, dtype=s64.dtype, count=s64.size) == s64)
                out.seek(HEAD_SIZE)
                assert np.min(
                    np.fromfile(out, dtype=stat_head.dtype, count=stat_head.size)
                    == stat_head
                )
            else:
                i4.tofile(out)
                f4.tofile(out)
                s64.tofile(out)
                out.seek(HEAD_SIZE)
                stat_head.tofile(out)

    def unfinished(out_file):
        try:
            with open(out_file, "rb") as hff:
                hff.seek(HEAD_SIZE)
                # checkpoints are vs and e_dist written to file
                # assume continuing machine is the same endian
                checkpoints = (
                    np.fromfile(
                        hff,
                        count=stations.size,
                        dtype={
                            "names": ["e_dist"],
                            "formats": ["f4"],
                            "offsets": [16],
                            "itemsize": HEAD_STAT,
                        },
                    )["e_dist"]
                    > 0
                )
        except IOError:
            # file not created yet
            return
        if checkpoints.size < stations.size:
            # file size is too short (simulation not even started properly)
            return
        if os.stat(args.out_file).st_size > file_size:
            # file size is too long (probably different simulation)
            return
        if np.min(checkpoints):
            try:
                logger.debug("Checkpoints found.")
                initialise(check_only=True)
                logger.error("HF Simulation already completed.")
                comm.Abort(1)
            except AssertionError:
                return
        # seems ok to continue simulation
        return np.invert(checkpoints)

    station_mask = None
    if is_master:
        station_mask = unfinished(args.out_file)
        if station_mask is None or sum(station_mask) == stations.size:
            logger.debug("No valid checkpoints found. Starting fresh simulation.")
            initialise()
            station_mask = np.ones(stations.size, dtype=bool)
        else:
            try:
                initialise(check_only=True)
                logger.info(
                    "{} of {} stations completed. Resuming simulation.".format(
                        stations.size - sum(station_mask), stations.size
                    )
                )
            except AssertionError:
                logger.warning(
                    "Simulation parameters mismatch. Starting fresh simulation."
                )
                initialise()
                station_mask = np.ones(stations.size, dtype=bool)
    station_mask = comm.bcast(station_mask, root=master)
    stations_todo = stations[station_mask]
    stations_todo_idx = np.arange(stations.size)[station_mask]

    def run_hf(
        local_statfile, n_stat, idx_0, v1d_path=args.hf_vel_mod_1d, bin_mod=True
    ):
        """
        Runs HF Fortran code.
        """
        if args.seed >= 0:
            assert n_stat == 1
            seed = args.seed + idx_0
        else:
            seed = random_seed()

        logger.info(
            "run_hf({}, {}, {}) seed: {}".format(local_statfile, n_stat, idx_0, seed)
        )

        hf_sim_args = [
            "",
            str(args.sdrop),
            local_statfile,
            args.out_file,
            "{:d} {}".format(len(args.rayset), " ".join(map(str, args.rayset))),
            str(int(not args.no_siteamp)),
            "{:d} {:d} {} {}".format(nbu, ift, flo, fhi),
            str(seed),
            str(n_stat),
            "{} {} {} {} {}".format(
                args.duration, args.dt, args.fmax, args.kappa, args.qfexp
            ),
            "{} {} {} {} {}".format(
                args.rvfac, args.rvfac_shal, args.rvfac_deep, args.czero, args.calpha
            ),
            "{} {}".format(args.mom, args.rupv),
            args.stoch_file,
            v1d_path,
            str(args.vs_moho),
            "{:d} {} {} {} {} {:d}".format(
                nl_skip, vp_sig, vsh_sig, rho_sig, qs_sig, ic_flag
            ),
            velocity_name,
            "{} {} {}".format(args.fa_sig1, args.fa_sig2, args.rv_sig1),
            str(args.path_dur),
        ]

        # extra params needed for v6.0
        if utils.compare_versions(args.version, "6.0.3") >= 0:
            hf_sim_args.append(
                "{} {} {}".format(
                    args.stress_param_adj[0],
                    args.stress_param_adj[1],
                    args.stress_param_adj[2],
                )
            )
        # add seekbyte for qcore adjusted version
        if bin_mod:
            # Only add the dpath_perturbation for versions that has the tail version of .4
            if (
                utils.compare_versions(args.version, "5.4.5.4") >= 0
                and len(args.version.split(".")) >= 4
                and utils.compare_versions(args.version.split(".")[3], "4") == 0
            ):
                hf_sim_args.append(str(args.dpath_pert))
            hf_sim_args.append(str(head_total + idx_0 * (nt * N_COMP * FLOAT_SIZE)))

        # add empty '' for extra \n at the end( needed as input)
        hf_sim_args.append("")

        stdin = "\n".join(hf_sim_args)

        logger.debug(stdin)

        # run HF binary
        p = Popen([args.sim_bin], stdin=PIPE, stderr=PIPE, universal_newlines=True)
        stderr = p.communicate(stdin)[1]

        # load vs
        with open(v1d_path, "r") as f:
            f.readline()
            vs = np.float32(float(f.readline().split()[2]) * 1000.0)

        # e_dist is the only other variable that HF calculates
        e_dist = np.fromstring(stderr, dtype="f4", sep="\n")
        try:
            assert e_dist.size == n_stat
        except AssertionError:
            logger.error(
                "Expected {} e_dist values, got {}".format(n_stat, e_dist.size)
            )
            logger.error("Dumping Fortran stderr to hf_err_{}".format(idx_0))

            with open(f"hf_err_{idx_0}", "w") as e:
                e.write(stderr)
            comm.Abort(1)

        # write e_dist and vs to file
        with open(args.out_file, "r+b") as out:
            out.seek(HEAD_SIZE + idx_0 * HEAD_STAT)
            for i in range(n_stat):
                out.seek(HEAD_STAT - 2 * FLOAT_SIZE, 1)
                e_dist[i].tofile(out)
                vs.tofile(out)

    # distribute work in a round-robin fashion across ranks for optimisation
    # if size=4, rank 0 takes [0,4,8...], rank 1 takes [1,5,9...], rank 2 takes [2,6,10...],
    # rank 3 takes [3,7,11...]
    work = stations_todo[rank::size]
    work_idx = stations_todo_idx[rank::size]

    # process data to give Fortran code
    t0 = MPI.Wtime()
    in_stats = mkstemp()[1]

    v1d_path = args.hf_vel_mod_1d
    for s in range(work.size):
        if args.site_specific:
            v1d_path = os.path.join(
                args.site_v1d_dir, f"{work[s]['name'].decode('ascii')}.1d"
            )

        np.savetxt(
            in_stats, work[s : s + 1], fmt="%f %f %s"
        )  # making in_stats file with the list of one station work[s]
        run_hf(
            in_stats, 1, work_idx[s], v1d_path=v1d_path
        )  # passing in_stat with the seed adjustment work_idx[s]

    os.remove(in_stats)
    logger.debug(
        "Process {} of {} completed {} stations ({:.2f}).".format(
            rank, size, work.size, MPI.Wtime() - t0
        )
    )
    comm.Barrier()  # all ranks wait here until rank 0 arrives to announce all completed
    if is_master:
        actual_size = os.stat(args.out_file).st_size
        if actual_size != file_size:
            msg = f"CRITICAL: Final file size mismatch! Expected {file_size}, got {actual_size}"
            print(msg, flush=True)
            logger.error(msg)
            comm.Abort(1)
        else:
            logger.debug("Simulation completed and size verified.")
            print("✅ HF completed successfully", flush=True)
