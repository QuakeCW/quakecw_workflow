"""Script to check that the LF seis files can be read.
Also checks a random (unless specified otherwise) station velocities for zeros,
which indicates a dual access issue (occurss when two EMOD3D processes for the
same sim run at the same time)
"""
import argparse
import numpy as np

from qcore.timeseries import LFSeis


def lf_zero_check(lf_data: LFSeis, station_ix: int = None):
    """
    Checks the specified station and velocity component for zeros. A random station
    and velocity component if these are not specified.

    Returns
    -------
    True if there are no zeros, otherwise False.
    """
    if station_ix is None:
        station_ix = np.random.choice(lf_data.stations.shape[0])

    vel = lf_data.vel(lf_data.stations.name[station_ix])

    if np.any(vel == 0.0):
        print(
            "The velocities for station {} contains zero/s, please investigate. This "
            "is most likely due to file access issues (such as several EMOD3D "
            "instances for the same sim).".format(lf_data.stations.name[station_ix])
        )
        return False

    return True


def main(args):
    try:
        lf_data = LFSeis(args.outbin)
    except Exception as ex:
        print(
            "At least one file of the OutBin/seis files fails the integrity check, with exception\n{}".format(
                ex
            )
        )
        return False
    else:
        return lf_zero_check(lf_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("outbin", type=str, help="The OutBin directory to test")
    args = parser.parse_args()

    if main(args):
        exit(0)
    exit(1)
