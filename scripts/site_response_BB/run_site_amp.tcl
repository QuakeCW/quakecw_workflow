if { $argc != 3 } {
    puts "The add.tcl script requires arguments."
    puts "For example, OpenSees run_site_amp.tcl ground_motion_path site_parameter_path output_directory"
    puts "Please try again."
    exit
} else {
    set gMotion [lindex $argv 0]
    puts "gMotion = $gMotion"

    set param_path [lindex $argv 1]
    puts "PARAM_PATH = $param_path"

    set output_dir [lindex $argv 2]
    puts "output_dir = output_dir"

}

# Load all the site specific parameters
source $param_path

# Run the simulation
source [file join [file dirname [info script]] site_amp_inner_loop.tcl]
wipe


