export PROJECT="$HOME/project"
export SCRATCH="/scratch/$USER"
export CW="$PROJECT/cw"
export QUAKECW="$CW/quakecw_workflow"
export gmsim="$CW"

export GMT_DIR="$PROJECT/local/gmt"
export GMT_DATADIR="$GMT_DIR/share"
export HDF5_DIR="$PROJECT/local/hdf5"
export SQLITE_DIR="$PROJECT/local/sqlite"
export GDAL_HOME="$PROJECT/local/gdal"
export GDAL_DATA="$GDAL_HOME/share/gdal"
export GDAL_CONFIG="$GDAL_HOME/bin/gdal-config"

export LD_LIBRARY_PATH="$PROJECT/local/fftw/lib:$PROJECT/local/OpenBLAS/lib:$HDF5_DIR/lib:$PROJECT/local/spatialindex/lib:$GMT_DIR/lib64:$SQLITE_DIR/lib:$GDAL_HOME/lib:$PROJECT/local/proj/lib:$PROJECT/local/curl/lib:$LD_LIBRARY_PATH"
export PKG_CONFIG_PATH="$PROJECT/local/fftw/lib/pkgconfig:$PROJECT/local/OpenBLAS/lib/pkgconfig:$SQLITE_DIR/lib/pkgconfig:$PKG_CONFIG_PATH"
export PYTHONPATH="$CW/Pre-processing:$PYTHONPATH"
export PATH="$PROJECT/local/sqlite/bin:$PROJECT/bin:$PROJECT/local/rclone-v1.73.5-linux-amd64:$PROJECT/EMOD3D/tools:$GMT_DIR/bin:$GDAL_HOME/bin:$PATH"

export BIN_DIR="$PROJECT/EMOD3D/tools"
export VELOCITY_MODEL_DIR="$CW/VelocityModel"
export VENV_DIR="$HOME/.local/quakecw_venv"

export PROMPT='${debian_chroot:+($debian_chroot)}\u@\h: \w\$ '

PS1=$PROMPT

shopt -u progcomp
shopt -s direxpand

module load gcc/10.2.0 openmpi/3.1.0 craype-mic-knl libxc cmake netcdf

alias tree='find . | sed -e "s/[^-][^\/]*\// |/g" -e "s/|\([^ ]\)/|-\1/"'

