import argparse
import subprocess
import dataclasses
import pathlib
import tempfile
import typing

import numpy as np
from numpy import fft
from scipy.integrate import _quadrature

from qcore import config, constants, qclogging, siteamp_models, timeseries, utils

BASE_COMPONENTS = [
    constants.Components.c000,
    constants.Components.c090,
    constants.Components.cver,
]
CM_TO_M_MULTIPLIER = 1.0 / 100

vs_ref = 500.0  # reference Vs at the ground surface in the HF GM simulation (m/s)
vp_ref = 1800.0  # reference Vp at the ground surface in the HF GM simulation (m/s)
rho_ref = 1810.0  # reference density at ground surface in the HF GM simulation (kg/m3)
vs_pga = vs_ref
vp_pga = vp_ref

# anelastic attenuation - according to GP2010
Qs = 50.0 * vs_ref / 1000.0  # quality factor - shear (dimensionless)
Qp = 2.0 * Qs  # quality factor - compression (dimensionless)
dampS_soil = 1.0 / (2.0 * Qs)  # damping ratio - shear (dimensionless)
dampP_soil = 1.0 / (2.0 * Qp)  # damping ratio - compression (dimensionless)

SITE_AMP_SCRIPT = pathlib.Path(__file__).parent / "run_site_amp.tcl"


@dataclasses.dataclass
class SiteProp:
    """
    Dataclass to hold the site properties for a location to run site response at a given location
    """

    H_soil: float  # Depth to bottom of soil column
    dampS_base: float  # Vs damping ratio of layer to which you deconvolve

    numLayers: int  # number of soil layers (not counting layer 0 which is bedrock)
    waterTable: float  # if water not present set waterTable anywhere below depth of model

    # allow excess pore pressure generation? Yes or No
    # If No, permeability is automatically set very high for dynamic analysis
    allowPWP: bool

    gammaPeak: float  # peak shear strain

    # flags for water table and Vs inversion
    # set VsInvTopLayer to "Yes" if there is a velocity inversion immediately below upper layer (else "No")
    # set waterTopLayer to "Yes" if water table within upper most layer and layer was split in two (else "No")
    # if waterTopLayer == "Yes", should set refDepth(numLayers) = 1.0 and refDepth(numLayers-1) = 0.0
    VsInvTopLayer: bool
    waterTopLayer: bool

    layerThick: typing.List[float]  # layer thicknesses

    # reference pressure
    # computed as mean confining pressure at refDepth for each layer (0 is ToL, 1 is BoL)
    refDepth: typing.List[float]

    rho: typing.List[float]  # soil mass density (Mg/m^3)
    Vs: typing.List[float]  # soil shear wave velocity for each layer(m/s)
    phi: typing.List[float]  # soil friction angle
    pressCoeff: typing.List[float]  # pressure dependency coefficient
    voidR: typing.List[float]  # void ratio (need it for layer 0 for element definition)

    phaseAng: typing.List[float]  # phase transformation angle (not for layer 0)

    # contraction (not for layer 0)
    contract1: typing.List[float]
    contract3: typing.List[float]

    # dilation coefficients (not for layer 0)
    dilate1: typing.List[float]
    dilate3: typing.List[float]

    name: str = ""  # Name of the station

    @property
    def soil_thick(self):
        return sum(self.layerThick)

    @property
    def rho_base(self):
        """Must convert from Mg/m^2 to kg/m^3"""
        return self.rho[0] * 1000

    @property
    def vs_base(self):
        return self.Vs[0]

    def __post_init__(self):
        assert len(self.rho) == self.numLayers + 1, f"{self.rho}, {self.numLayers + 1}"
        assert len(self.Vs) == self.numLayers + 1, f"{self.Vs}, {self.numLayers + 1}"
        assert len(self.phi) == self.numLayers + 1, f"{self.phi}, {self.numLayers + 1}"
        assert (
            len(self.pressCoeff) == self.numLayers + 1
        ), f"{self.pressCoeff}, {self.numLayers + 1}"
        assert (
            len(self.voidR) == self.numLayers + 1
        ), f"{self.voidR}, {self.numLayers + 1}"
        assert (
            len(self.phaseAng) == self.numLayers
        ), f"{self.phaseAng}, {self.numLayers}"
        assert (
            len(self.contract1) == self.numLayers
        ), f"{self.contract1}, {self.numLayers}"
        assert (
            len(self.contract3) == self.numLayers
        ), f"{self.contract3}, {self.numLayers}"
        assert len(self.dilate1) == self.numLayers, f"{self.dilate1}, {self.numLayers}"
        assert len(self.dilate3) == self.numLayers, f"{self.dilate3}, {self.numLayers}"

    @staticmethod
    def from_file(file_path):
        """Loads the station yaml file"""
        return SiteProp(**utils.load_yaml(file_path), name=pathlib.Path(file_path).stem)

    def to_tcl(self, file_path, nt=None):
        """
        Writes the site properties in tcl format, as required by the site amplification code
        :param file_path: The path to write the file to
        :param nt: The number of time steps. Added for convenience.
            If more non-site parameters are needed, make a new file
        """

        def list_to_tcl(val, offset=0):
            """Converts a list into tcl compatible array list format"""
            return " ".join([f"{i+offset} {x}" for i, x in enumerate(val)])

        def bool_to_tcl(val):
            """Converts a bool into tcl compatible equivalent"""
            return "Yes" if val else "No"

        out_str = f"""
# Scalars
set numLayers {self.numLayers}
set soilThick {self.soil_thick}
set waterTable {self.waterTable}
set gammaPeak {self.gammaPeak}

# Bools
set allowPWP {bool_to_tcl(self.allowPWP)}                
set VsInvTopLayer {bool_to_tcl(self.VsInvTopLayer)}
set waterTopLayer {bool_to_tcl(self.waterTopLayer)}

# Arrays
array set layerThick [list {list_to_tcl(self.layerThick)}]
array set refDepth [list {list_to_tcl(self.refDepth)}]
array set rho [list {list_to_tcl(self.rho)}]
array set Vs [list {list_to_tcl(self.Vs)}]
array set phi [list {list_to_tcl(self.phi)}]
array set pressCoeff [list {list_to_tcl(self.pressCoeff)}]
array set phaseAng [list {list_to_tcl(self.phaseAng, 1)}]
array set contract1 [list {list_to_tcl(self.contract1, 1)}]
array set contract3 [list {list_to_tcl(self.contract3, 1)}]
array set dilate1 [list {list_to_tcl(self.dilate1, 1)}]
array set dilate3 [list {list_to_tcl(self.dilate3, 1)}]
array set voidR [list {list_to_tcl(self.voidR)}]
"""

        if nt is not None:
            out_str += f"\nset motionSteps {nt}"

        with open(file_path, "w") as fp:
            fp.write(out_str)


class TimeOutError(Exception):
    pass


def cumulative_trapezoid(y, dx=1.0, initial=0):
    """
    Cumulatively integrate y(x) using the composite trapezoidal rule.

    Parameters
    ----------
    y : array_like
        Values to integrate.
    dx : float, optional
        Spacing between elements of `y`. Only used if `x` is None.
    initial : scalar, optional
        If given, insert this value at the beginning of the returned result.
        Typically this value should be 0. Default is None, which means no
        value at ``x[0]`` is returned and `res` has one element less than `y`
        along the axis of integration.

    Returns
    -------
    res : ndarray
        The result of cumulative integration of `y` along `axis`.
        If `initial` is None, the shape is such that the axis of integration
        has one less value than `y`. If `initial` is given, the shape is equal
        to that of `y`.

    Note: Copied from numpy source, as function not present in Python3.6 compatible versions of numpy
    """
    y = np.asarray(y)
    nd = len(y.shape)
    slice1 = _quadrature.tupleset((slice(None),) * nd, -1, slice(1, None))
    slice2 = _quadrature.tupleset((slice(None),) * nd, -1, slice(None, -1))
    res = np.cumsum(dx * (y[slice1] + y[slice2]) / 2.0, axis=-1)

    shape = list(res.shape)
    shape[-1] = 1
    res = np.concatenate([np.full(shape, initial, dtype=res.dtype), res], axis=-1)

    return res


def run_deamp(waveform, component: constants.Components, dt, vs_site, hf_pga):
    """
    Performs Hanning tapering and applies a deamplification factor to the input timeseries
    :param waveform: timeseries in cm/s/s
    :param component: The component the timeseries is for. Currently not used
    :param dt: The time step of the input timeseries
    :param vs_site: the Vs value of the site
    :param hf_pga: The PGA of the HF component of the input waveform
    :return: A timeseries with the Hanning tapering and deamplification applied in cm/s/s
    """
    npts = waveform.size
    # Fourier transform of the acceleration time history of the BBGM simulation
    # length for fft and Nyquist frequency
    ft_len = int(2.0 ** np.ceil(np.log2(npts)))
    # apply taper to BBGM simulation on 5% values on the right using the Hanning method
    ntap = int(npts * 0.05)
    waveform[npts - ntap :] *= np.hanning(ntap * 2 + 1)[ntap + 1 :]
    # extend with blanks for the fft
    waveform.resize(ft_len, refcheck=False)
    ft = fft.rfft(waveform)

    # compute the amplification factor from CB14, take inverse, and...
    # "remove" it from the BBGM simulation
    # TODO: have multiple deamp functions
    if component in [constants.Components.c000, constants.Components.c090]:
        ampf = siteamp_models.cb_amp(dt, ft_len, vs_ref, vs_site, vs_pga, hf_pga)
    else:  # TODO we should have different site amp for hor and ver components
        ampf = siteamp_models.cb_amp(dt, ft_len, vs_ref, vs_site, vs_pga, hf_pga)
    ft[:-1] *= 1.0 / ampf
    return fft.irfft(ft)[:npts]


def deconvolve_timeseries_and_run_site_response(
    acceleration_waveform: np.ndarray,
    component: constants.Components,
    site_properties: SiteProp,
    dt=0.005,
    logger=qclogging.get_basic_logger(),
):
    """
    Deconvolves a surface waveform to a waveform at a given depth
    No deamplification occurs here
    :param acceleration_waveform: a 1d array of the component velocities to be run in cm/s/s
    :param component: The name of the component. Used to determine the transfer function to use
    :param site_properties: A SiteProp object for the location
    :param dt: The timestep for the given waveform
    :param logger: Logger to send messages to
    :return: A waveform with site specific amplification applied. Has the same shape as waveform and units of m/s/s
    """
    size = acceleration_waveform.size

    ntap = int(size * 0.05)
    acceleration_waveform[size - ntap :] *= np.hanning(ntap * 2 + 1)[ntap + 1 :]

    ft_len = int(2.0 ** np.ceil(np.log2(size)))
    acceleration_waveform = acceleration_waveform.copy()
    acceleration_waveform.resize(ft_len, refcheck=False)

    if component in BASE_COMPONENTS[:2]:
        transfer = timeseries.transf(
            vs_ref,
            rho_ref,
            dampS_soil,
            site_properties.H_soil,
            site_properties.vs_base,
            site_properties.rho_base,
            site_properties.dampS_base,
            acceleration_waveform.size,
            dt,
        )
    elif component is constants.Components.cver:
        # TODO: Get ver transfer function
        transfer = timeseries.transf(
            vp_ref,
            rho_ref,
            dampP_soil,
            site_properties.H_soil,
            site_properties.vs_base,
            site_properties.rho_base,
            site_properties.dampS_base,
            acceleration_waveform.size,
            dt,
        )
    else:
        raise ValueError(
            f"Invalid component selected. "
            f"Only {[comp.str_value for comp in BASE_COMPONENTS]} are valid. "
            f"{component} is not."
        )

    waveform_ft = np.fft.rfft(acceleration_waveform)
    deconv_ft = (1.0 / transfer) * waveform_ft
    bbgm_decon = np.fft.irfft(deconv_ft)[:size]

    # integrate acceleration to get velocity (in m/s) for input to OpenSees
    bbgm_decon_vel = (
        cumulative_trapezoid(bbgm_decon, dx=dt, initial=0) * CM_TO_M_MULTIPLIER
    )

    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        with tempfile.NamedTemporaryFile(dir=td) as file_name:
            # File name doesn't matter for temp file
            np.savetxt(file_name, bbgm_decon_vel)
            params_path = td / "params.tcl"
            site_properties.to_tcl(params_path, nt=size)
            try:
                out_file = call_opensees(file_name.name, params_path, td, logger=logger)
            except RuntimeError as e:
                logger.error(f"This didn't work: {component}, {site_properties.name}")
                raise e
            else:
                # Acceleration in m/s/s
                return np.loadtxt(out_file)


def check_status(component_outdir, check_fail=False):
    """
    check the status of a run by scanning Analysis_* for keyword: "Successful" / "Failed"
    check_fail: Bools. changes the keyword
    """

    analysis_files = list(pathlib.Path(component_outdir).glob("Analysis_*"))

    if len(analysis_files) == 0:
        return False

    if check_fail:
        keyword = "Failed"
        result = True
        for f in analysis_files:
            contents = f.read_text()
            result = result and (contents.strip() == keyword)
    else:
        keyword = "Successful"
        result = False
        for f in analysis_files:
            contents = f.read_text()
            result = result or (contents.strip() == keyword)
    return result


def call_opensees(
    input_file,
    params_path,
    out_dir,
    timeout_threshold=600,
    logger=qclogging.get_basic_logger(),
):
    script = [
        config.qconfig["OpenSees"],
        SITE_AMP_SCRIPT,
        input_file,
        params_path,
        out_dir,
    ]

    try:
        subp = subprocess.run(
            script,
            timeout=timeout_threshold,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.TimeoutExpired as e:
        logger.error(str(e))
        raise e

    logger.debug(f'got stdout line from subprocess: {subp.stdout.decode("utf-8")}')
    logger.debug(f'got stderr line from subprocess: {subp.stderr.decode("utf-8")}')

    out_file_path = out_dir / "out.txt"
    return out_file_path


def run_deamp_decon_and_site_response_ascii(folder, station_folder, output_dir):

    files = folder.glob("*.*")
    stations = {x.stem for x in files}

    sites = {
        station.stem: station
        for station in station_folder.iterdir()
        if station.stem in stations
    }

    for site_name, site_path in sites.items():
        site_prop = SiteProp.from_file(site_path)
        for i, waveform_component in enumerate(BASE_COMPONENTS):
            vel_waveform, meta = timeseries.read_ascii(
                folder / f"{site_name}.{waveform_component.str_value}", meta=True
            )
            acc_waveform = timeseries.vel2acc(vel_waveform, meta["dt"])
            deamp_wave = run_deamp(
                acc_waveform,
                waveform_component,
                meta["dt"],
                site_prop.Vs[0],
                np.max(acc_waveform),
            )
            deconv = deconvolve_timeseries_and_run_site_response(
                deamp_wave[:], waveform_component, site_prop, meta["dt"]
            )
            np.savetxt(
                output_dir / f"{site_name}_{waveform_component.str_value}.csv",
                deconv,
            )


def run_deamp_decon_and_site_response_binary(bb_bin, station_folder, output_dir):

    bb = timeseries.BBSeis(bb_bin)
    dt = bb.dt

    sites = {
        station.stem: station
        for station in station_folder.iterdir()
        if station.stem in bb.stations
    }

    for site_name, site_path in sites.items():
        site_prop = SiteProp.from_file(site_path)
        acc_waveforms = bb.acc(site_name) * 980.665  # Convert g to cm/s/s
        for i, waveform_component in enumerate(BASE_COMPONENTS):
            deamp_wave = run_deamp(
                acc_waveforms[i],
                waveform_component,
                dt,
                site_prop.Vs[0],
                np.max(acc_waveforms[i]),  # ????
            )
            deconv = deconvolve_timeseries_and_run_site_response(
                deamp_wave[:], waveform_component, site_prop, dt
            )
            np.savetxt(
                output_dir / f"{site_name}_{waveform_component.str_value}.csv",
                deconv,
            )


def load_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "bb_bin",
        type=pathlib.Path,
        help="Either folder of ascii waveforms or binary BB.bin files",
    )
    parser.add_argument(
        "station_folder", type=pathlib.Path, help="Folder with site data"
    )
    parser.add_argument(
        "output_dir", type=pathlib.Path, help="Location to save output values"
    )
    parser.add_argument(
        "--type",
        default="a",
        choices=["a", "b"],
        help="Type of input data, either (a)scii or (b)inary.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = load_args()
    if args.type == "a":
        run_deamp_decon_and_site_response_ascii(
            args.bb_bin, args.station_folder, args.output_dir
        )
    elif args.type == "b":
        run_deamp_decon_and_site_response_binary(
            args.bb_bin, args.station_folder, args.output_dir
        )
