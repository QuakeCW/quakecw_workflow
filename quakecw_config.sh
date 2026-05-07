export PROJECT="$HOME/project"
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

export LD_LIBRARY_PATH="$PROJECT/local/fftw/lib:$PROJECT/local/OpenBLAS/lib:$HDF5_DIR/lib:$PROJECT/local/spatialindex/lib:$GMT_DIR/lib:$SQLITE_DIR/lib:$GDAL_HOME/lib:$PROJECT/local/proj/lib:$PROJECT/local/curl/lib:$LD_LIBRARY_PATH"
export PKG_CONFIG_PATH="$PROJECT/local/fftw/lib/pkgconfig:$PROJECT/local/OpenBLAS/lib/pkgconfig:$SQLITE_DIR/lib/pkgconfig:$PKG_CONFIG_PATH"
export PYTHONPATH="$CW/Pre-processing:$PYTHONPATH"
export PATH="$PROJECT/local/sqlite/bin:$PROJECT/bin:$PROJECT/EMOD3D/tools:$GMT_DIR/bin:$GDAL_HOME/bin:$PATH"

export BIN_DIR="$PROJECT/EMOD3D/tools"
export VELOCITY_MODEL_DIR="$CW/VelocityModel"
export VENV_DIR="$HOME/.local/quakecw_venv"

