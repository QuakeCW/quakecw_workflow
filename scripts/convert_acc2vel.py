import os
import numpy as np
from qcore import timeseries

def convert_acc_to_vel(acc_folder="Obs_Acc", vel_folder="Obs_Vel"):
    """Convert all .000, .090, .ver files from Obs_Acc to Obs_Vel"""

    # Create output folder if it doesn't exist
    if not os.path.exists(vel_folder):
        os.makedirs(vel_folder)

    # Get all station files from Obs_Acc
    acc_files = [f for f in os.listdir(acc_folder) if f.endswith(('.000', '.090', '.ver'))]

    for acc_file in acc_files:
        acc_path = os.path.join(acc_folder, acc_file)
        vel_path = os.path.join(vel_folder, acc_file)

        # Read acceleration
        acc_ts = timeseries.read_ascii(acc_path)

        # Get dt from metadata (or just pass it)
        # Note: read_ascii without meta returns just the array
        # You might need to read with meta=True to get dt

        # Simple approach - read with metadata
        acc_ts, meta = timeseries.read_ascii(acc_path, meta=True)
        dt = meta['dt']

        # Convert to velocity using the function you showed
        vel_ts = timeseries.acc2vel(acc_ts, dt)

        # Save to Obs_Vel folder (preserving the same format)
        timeseries.timeseries_to_text(
            vel_ts,
            vel_path,
            dt,
            meta['name'],
            meta['comp'],
            start_hr=meta['hr'],
            start_min=meta['min'],
            start_sec=meta['sec'],
            edist=meta['e_dist'],
            az=meta['az'],
            baz=meta['baz']
        )

        print(f"Converted: {acc_file}")

if __name__ == "__main__":
    # Check if Obs_Acc exists in current directory
    if not os.path.exists("Obs_Acc"):
        print("Error: Obs_Acc folder not found in current directory")
        print(f"Current directory: {os.getcwd()}")
        print("Contents:", os.listdir('.'))
        sys.exit(1)

    convert_acc_to_vel()

