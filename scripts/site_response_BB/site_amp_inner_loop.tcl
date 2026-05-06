###########################################################
#                                                         #
# Effective Stress Site Response Analysis
# Pressure Independent Vs Profile
# Constitutive Model: PDMY02
# Pore Pressure Generation Allowed: No
#
# Strong Motion Station: REHS
#                                                          #
###########################################################

#-----------------------------------------------------------------------------------------
#  1. DEFINE SOIL GEOMETERY AND MATERIAL PARAMETERS
#-----------------------------------------------------------------------------------------

#---MATERIAL PROPERTIES
# define gravity and pi
set g 9.80665
set pi [expr atan(1)*4]
set rhoWater       1.0


# define layer boundaries
set layerBound(0) $layerThick(0)
puts "layer boundary 0 = $layerBound(0)"
for {set i 1} {$i <= $numLayers} {incr i 1} {
    set layerBound($i) [expr $layerBound([expr $i-1])+$layerThick($i)]
    puts "layer boundary $i = $layerBound($i)"
}

    ## for top layer
if {$layerThick($numLayers) > $waterTable} {
    set vertStress($numLayers) [expr ($rho($numLayers) - $rhoWater) * $g * $layerThick($numLayers) * $refDepth($numLayers)]
}   else {
    set vertStress($numLayers) [expr $rho($numLayers) * $g * $layerThick($numLayers) * $refDepth($numLayers)]
}
set kNot($numLayers) [expr (1.0 - sin($phi($numLayers) * 2.0 * $pi / 360.0))]
set meanStress [expr $vertStress($numLayers) * (1.0 + 2.0 * $kNot($numLayers)) / 3.0]
set refPress($numLayers) $meanStress

## for other layers (not necessary for layer 0 bc it's lin elastic bedrock)
set bottomDepth($numLayers) $layerThick($numLayers)

for {set k [expr $numLayers - 1]} {$k > 0 && $k <= [expr $numLayers - 1]} {incr k -1} {
    set bottomDepth($k) [expr $bottomDepth([expr $k + 1]) + $layerThick($k)]
    if {$bottomDepth($k) > $waterTable && $bottomDepth([expr $k + 1]) > $waterTable} {
 	    set vertStress($k) [expr $vertStress([expr $k + 1]) + ($rho([expr $k + 1]) - $rhoWater) * $g * $layerThick([expr $k + 1]) * (1.0 - $refDepth([expr $k + 1])) + ($rho($k) - $rhoWater) * $g * $layerThick($k) * $refDepth($k)]
    } elseif {$bottomDepth($k) > $waterTable} {
        set vertStress($k) [expr $vertStress([expr $k + 1]) + $rho([expr $k + 1]) * $g * $layerThick([expr $k + 1]) * (1.0 - $refDepth([expr $k + 1])) + ($rho($k) - $rhoWater) * $g * $layerThick($k) * $refDepth($k)]
    } else {
        set vertStress($k) [expr $vertStress([expr $k + 1]) + $rho([expr $k + 1]) * $g * $layerThick([expr $k + 1]) * (1.0 - $refDepth([expr $k + 1])) + $rho($k) * $g * $layerThick($k) * $refDepth($k)]
}
	set kNot($k) [expr 1.0 - sin($phi($k) * 2.0 * $pi / 360.0)]
	set meanStress [expr $vertStress($k) * (1.0 + 2.0 * $kNot($k)) / 3.0]
	set refPress($k) $meanStress
}

# compute Vs_not, the constant required for an exponential function of Vs to have
# equal travel time to a layer of constant Vs
set Vs_not [expr $Vs($numLayers)*pow($layerThick($numLayers), -$pressCoeff($numLayers) / 2.0) / (1.0 - $pressCoeff($numLayers) / 2.0)]
puts "Vs_not = $Vs_not"
 
# soil shear modulus for each layer (kPa)
    # for top layer
if {$VsInvTopLayer == "Yes" || $waterTopLayer == "Yes"} {
    set G($numLayers) [expr $rho($numLayers)*$Vs($numLayers)*$Vs($numLayers)]
    } else {
       set G($numLayers) [expr $rho($numLayers) * pow($Vs_not, 2.0 ) * pow($rho($numLayers) * $g  * (1.0 + 2.0 * $kNot($numLayers)) / (3.0 * $refPress($numLayers)), -$pressCoeff($numLayers)) ]
}
    # for all other layers    
for {set k 0} {$k < $numLayers} {incr k 1} {
    set G($k) [expr $rho($k)*$Vs($k)*$Vs($k)]    
}
# poisson's ratio of soil
set nu              0.25
# soil elastic modulus for each layer (kPa)
for {set k 0} {$k <= $numLayers} {incr k 1} {
    set E($k)       [expr 2*$G($k)*(1+$nu)]
}
# soil bulk modulus for each layer (kPa)
for {set k 0} {$k <= $numLayers} {incr k 1} {
    set bulk($k)    [expr $E($k)/(3*(1-2*$nu))]
}

# Default parameters for PDMY02 as follows:
# Layer 6: Dr = 75%
# Layer 5: Dr = 40%
# Layer 4: Dr = 30% (using contract1 = 0.013 and contract3 = 0.000, nonliq silt)
# Layer 3: Dr = 30% (using contract1 = 0.013 and contract3 = 0.000, nonliq silt)
# Layer 2: Dr = 75% 
# Layer 1: Dr = 75% (using contract1 = 0.013 and contract3 = 0.000, nonliq silt)

# bedrock shear wave velocity (m/s)
set rockVS           $Vs(0)
# bedrock mass density (Mg/m^3)
set rockDen          $rho(0)

#-----------------------------------------------------------------------------------------
#  2. MESH GEOMETRY
#-----------------------------------------------------------------------------------------

#---MESH GEOMETRY
# highest frequency desired to be well resolved (Hz)
set fMax    25.0
# wavelength of highest resolved frequency for each layer
for {set k 0} {$k <= $numLayers} {incr k 1} {
	set wave($k) [expr $Vs($k)/$fMax]
}
# number of elements per one wavelength
set nEle     8

# Determine number of elements in column
set nElemT 0
for {set k 0} {$k <= $numLayers} {incr k 1} {
	# maximum element height
	set hEleMax($k) [expr $wave($k)/$nEle]
	
	# interger number of elements
	set nElemY($k) [expr int(floor($layerThick($k)/$hEleMax($k))+1)]
	puts "number of vertical elements in layer $k: $nElemY($k)"

	set nElemT [expr $nElemT + $nElemY($k)]

	# actual element height
	set sElemY($k) [expr {$layerThick($k)/$nElemY($k)}] 

        puts "vertical size of elements in layer $k: $sElemY($k)"
}
puts "total number of vertical elements: $nElemT"

# number of nodes in vertical direction
set nNodeY  [expr 2*$nElemT+1]

# number of elements in horizontal direction
set nElemX  1
# number of nodes in horizontal direction
set nNodeX  [expr 2*$nElemX+1]
# horizontal element size (m)
set sElemX  2.0

# total number of nodes
set nNodeT  [expr $nNodeX*$nNodeY]

#-----------------------------------------------------------------------------------------
#  3. CREATE PORE PRESSURE NODES AND FIXITIES
#-----------------------------------------------------------------------------------------
model BasicBuilder -ndm 2 -ndf 3

set ppNodesInfo [open $output_dir/ppNodesInfo.dat w]
set dryNodeCount 1
set PPNodeCount 1
set layerNodeCount 0
set yCoordCount 0
# loop over soil layers
for {set k 0} {$k <= $numLayers} {incr k 1} {
  # loop in horizontal direction
     for {set i 1} {$i <= $nNodeX} {incr i 2} {
      # loop in vertical direction
        if {$k == 0} {
            set bump 1
        } else {
            set bump 0
        }
        for {set j 1} {$j <= [expr 2*$nElemY($k)+$bump]} {incr j 2} {

            set xCoord       [expr ($i-1)*$sElemX/2.0]
            set yctr    [expr $j + $layerNodeCount]
            if {$k == 0} {
                set yCoord       [expr ($j-1)*$sElemY($k)/2.0]
          } else {
                set yCoord       [expr $layerBound([expr $k - 1]) + $sElemY($k) + ($j - 1)*$sElemY($k)/2.0]
          }
            set nodeNum      [expr $i + ($yctr-1)*$nNodeX]
            
            node $nodeNum  $xCoord  $yCoord

          # puts "yctr = $yctr"
          # puts "xCoord = $xCoord"
          # puts "yCoord = $yCoord"
          # puts "nodeNum = $nodeNum"
            
            set PPNode($PPNodeCount) $nodeNum
            set PPNodeCount [expr $PPNodeCount + 1]

          # output nodal information to data file
            puts $ppNodesInfo "$nodeNum  $xCoord  $yCoord"

          # designate nodes above water table
            set waterHeight [expr $soilThick-$waterTable]
            if {$yCoord>=$waterHeight} {
                set dryNode($dryNodeCount) $nodeNum
                set dryNodeCount [expr $dryNodeCount+1]
            }
        }
    }
   set layerNodeCount [expr $yctr + 1]
}
close $ppNodesInfo
puts "Finished creating all -ndf 3 nodes..."

# define fixities for pore pressure nodes above water table
for {set i 1} {$i < $dryNodeCount} {incr i 1} {
    fix $dryNode($i)  0 0 1
}

# define fixities for pore pressure nodes at base of soil column
fix 1  0 1 0
fix 3  0 1 0
puts "Finished creating all -ndf 3 boundary conditions..."


# define equal degrees of freedom for pore pressure nodes
for {set i 1} {$i <= [expr 3*$nNodeY-2]} {incr i 6} {
    equalDOF $i [expr $i+2]  1 2
}
puts "Finished creating equalDOF for pore pressure nodes..."

#-----------------------------------------------------------------------------------------
#  4. CREATE INTERIOR NODES AND FIXITIES
#-----------------------------------------------------------------------------------------
model BasicBuilder -ndm 2 -ndf 2

# central column of nodes
set xCoord  [expr $sElemX/2]
# loop over soil layers
set layerNodeCount 0
for {set k 0} {$k <= $numLayers} {incr k 1} {
  # loop in vertical direction
      if {$k == 0} {
        set bump 1
    } else {
        set bump 0
    }
    for {set j 1} {$j <= [expr 2 * $nElemY($k) + $bump]} {incr j 1} {

        set yctr    [expr $j + $layerNodeCount]
        if {$k == 0} {
            set yCoord  [expr ($j - 1) * $sElemY($k) / 2.0]
      } else {
            set yCoord  [expr $layerBound([expr $k - 1]) + $sElemY($k) / 2.0 +  ($j - 1) * $sElemY($k) / 2.0]
      }      
        set nodeNum [expr 3 * $yctr - 1] 

        node  $nodeNum  $xCoord  $yCoord 
    }
    set layerNodeCount $yctr
}

# interior nodes on the element edges
# loop over layers
set layerNodeCount 0
for {set k 0} {$k <= $numLayers} {incr k 1} {
  # loop in vertical direction
      for {set j 1} {$j <= $nElemY($k)} {incr j 1} {

        set yctr [expr $j + $layerNodeCount]
        if {$k == 0} {
            set yCoord   [expr $sElemY($k) * ($j - 0.5)]
      } else {
            set yCoord   [expr $layerBound([expr $k - 1]) + ($j - 0.5) * $sElemY($k)]
      }
        set nodeNumL [expr 6*$yctr - 2]
        set nodeNumR [expr $nodeNumL + 2]
    
        node  $nodeNumL  0.0  $yCoord
        node  $nodeNumR  $sElemX  $yCoord
    }
    set layerNodeCount $yctr
}
puts "Finished creating all -ndf 2 nodes..."

# define fixities for interior node at base of soil column
fix 2  0 1
puts "Finished creating all -ndf 2 boundary conditions..."

# define equal degrees of freedom which have not yet been defined
for {set i 1} {$i <= [expr 3*$nNodeY-6]} {incr i 6} {
    equalDOF $i          [expr $i+1]  1 2
    equalDOF [expr $i+3] [expr $i+4]  1 2
    equalDOF [expr $i+3] [expr $i+5]  1 2
}
equalDOF [expr $nNodeT-2] [expr $nNodeT-1]  1 2
puts "Finished creating equalDOF constraints..."


#-----------------------------------------------------------------------------------------
#  5. CREATE SOIL MATERIALS
#-----------------------------------------------------------------------------------------

# define grade of slope (%)
set grade 0.0
set slope [expr atan($grade/100.0)]
set g -9.81
set bulkWater 2.2e6

# define nonlinear material for soil
for {set i 1} {$i <= $numLayers} {incr i 1} {
    nDMaterial PressureDependMultiYield02 $i 2 $rho($i) $G($i) $bulk($i) $phi($i) $gammaPeak \
                                      $refPress($i) $pressCoeff($i) $phaseAng($i) \
                                      $contract1($i) $contract3($i) $dilate1($i) $dilate3($i) \
                                      20 5 3 1 0 $voidR($i) 0.9 0.02 0.7 101.0  

    set thick($i) 1.0
    set xWgt($i)  [expr $g*sin($slope)]
    set yWgt($i)  [expr $g*cos($slope)]
    set porosity($i) [expr $voidR($i) / (1 + $voidR($i))]
    set uBulk($i) [expr $bulkWater/$porosity($i)]
    set hPerm($i) 1.0e-4
    set vPerm($i) 1.0e-4


}
# define linear elastic material for "bedrock"
nDMaterial ElasticIsotropic 0 $E(0) 0.3 $rho(0)

set thick(0) 1.0
set xWgt(0)  [expr $g*sin($slope)]
set yWgt(0)  [expr $g*cos($slope)]
set porosity(0) [expr $voidR(0) / (1 + $voidR(0))]
set uBulk(0) [expr $bulkWater/$porosity(0)]
set hPerm(0) 1.0e-4
set vPerm(0) 1.0e-4

puts "Finished creating all soil materials..."

#-----------------------------------------------------------------------------------------
#  6. CREATE SOIL ELEMENTS
#-----------------------------------------------------------------------------------------

# define the top element number of each layer
set elemCount 0.0
set layerTopEleNum(-1) 0
for {set i 0} {$i <= $numLayers} {incr i 1} {
    set layerTopEleNum($i) [expr $elemCount + $nElemY($i)]
    set elemCount [expr $elemCount + $nElemY($i)]
}

for {set j 1} {$j <= $nElemT} {incr j 1} {

    set nI  [expr 6*$j - 5]
    set nJ  [expr $nI + 2]
    set nK  [expr $nI + 8]
    set nL  [expr $nI + 6]
    set nM  [expr $nI + 1]
    set nN  [expr $nI + 5]
    set nP  [expr $nI + 7]
    set nQ  [expr $nI + 3]
    set nR  [expr $nI + 4]

    set lowerBound 0.0
    for {set i 0} {$i <= $numLayers} {incr i 1} {

          if {$j <= $layerTopEleNum($i) && $j > $layerTopEleNum([expr $i - 1])} {

          # permeabilities are initially set at 10.0 m/s for gravity analysis, values are updated post-gravity
              element 9_4_QuadUP $j $nI $nJ $nK $nL $nM $nN $nP $nQ $nR \
                           $thick($i) $i $uBulk($i) 1.0 10.0 10.0 $xWgt($i) $yWgt($i)

              puts "element 9_4_QuadUP $j $nI $nJ $nK $nL $nM $nN $nP $nQ $nR $thick($i) $i $uBulk($i) 1.0 1.0 1.0 $xWgt($i) $yWgt($i)"

        }
        set lowerBound $layerBound($i)
    }
}
puts "Finished creating all soil elements..."

#-----------------------------------------------------------------------------------------
#  7. LYSMER DASHPOT
#-----------------------------------------------------------------------------------------

# define dashpot nodes
set dashF [expr $nNodeT+1]
set dashS [expr $nNodeT+2]

node $dashF  0.0 0.0
node $dashS  0.0 0.0

# define fixities for dashpot nodes
fix $dashF  1 1
fix $dashS  0 1

# define equal DOF for dashpot and base soil node
equalDOF 1 $dashS  1
puts "Finished creating dashpot nodes and boundary conditions..."

# define dashpot material
set colArea       [expr $sElemX*$thick(0)]
set dashpotCoeff  [expr $rockVS*$rockDen]
uniaxialMaterial Viscous [expr $numLayers+1] [expr $dashpotCoeff*$colArea] 1

# define dashpot element
element zeroLength [expr $nElemT+1]  $dashF $dashS -mat [expr $numLayers+1]  -dir 1
puts "Finished creating dashpot material and element..."

#-----------------------------------------------------------------------------------------
#  8. CREATE GRAVITY RECORDERS
#-----------------------------------------------------------------------------------------

# create list for pore pressure nodes
set nodeList3 {}
set channel [open "$output_dir/ppNodesInfo.dat" r]
set count 0;
foreach line [split [read -nonewline $channel] \n] {
    set count [expr $count+1];
    set lineData($count) $line
    set nodeNumber [lindex $lineData($count) 0]
    lappend nodeList3 $nodeNumber
}
set nodeList3 [lsort -integer $nodeList3]
close $channel

puts "Finished creating gravity recorders..."

#-----------------------------------------------------------------------------------------
#  9. DEFINE ANALYSIS PARAMETERS
#-----------------------------------------------------------------------------------------

#---GROUND MOTION PARAMETERS

# number of steps in ground motion record

# Temporary load of timeseries to determine nt
set mSeries "Path -dt 0.005 -filePath $gMotion"
# set motionSteps [expr int($simTime/0.005)]
# set motionSteps [llength $mSeries]

puts "duration = [expr $motionSteps*0.005] sec"

#---RAYLEIGH DAMPING PARAMETERS
set pi      3.141592654
# damping ratio
set damp    0.05
# lower frequency
set omega1  [expr 2*$pi*0.2]
# upper frequency
set omega2  [expr 2*$pi*20]
# damping coefficients
set a0      [expr 2*$damp*$omega1*$omega2/($omega1 + $omega2)]
set a1      [expr 2*$damp/($omega1 + $omega2)]
puts "damping coefficients: a_0 = $a0;  a_1 = $a1"

#---DETERMINE STABLE ANALYSIS TIME STEP USING CFL CONDITION
# maximum shear wave velocity (m/s)
set vsMax $Vs(0)
for {set i 1} {$i <= $numLayers} {incr i 1} {
    if {$Vs($i) > $vsMax} {
        set vsMax $Vs($i)
    }
}
# duration of ground motion (s)
set motionDT 0.005
set duration    [expr $motionDT*$motionSteps]
puts "Duration: $duration"
# minimum element size
set minSize $sElemY(0)
for {set i 1} {$i <= $numLayers} {incr i 1} {
    if {$sElemY($i) < $minSize} {
        set minSize $sElemY($i)
    }
}

# trial analysis time step
set kTrial      [expr $minSize/(pow($vsMax,0.5))]
# define time step and number of steps for analysis
if { $motionDT <= $kTrial } {
    set nSteps  $motionSteps
    set dT      $motionDT
} else {
    set nSteps  [expr int(floor($duration/$kTrial)+1)]
    set dT      [expr $duration/$nSteps]
}
puts "number of steps in analysis: $nSteps"
puts "analysis time step: $dT"

#---ANALYSIS PARAMETERS
# Newmark parameters
set gamma           0.5
set beta            0.25

#-----------------------------------------------------------------------------------------
#  10. GRAVITY ANALYSIS
#-----------------------------------------------------------------------------------------

# update materials to ensure elastic behavior
for {set k 1} {$k <= $numLayers} {incr k} {
    updateMaterialStage -material $k -stage 0
}

constraints Penalty 1.e14 1.e14
test        NormDispIncr 1e-6 35 1
algorithm   KrylovNewton
numberer    RCM
system      ProfileSPD
integrator  Newmark $gamma $beta

analysis    Transient

set startT  [clock seconds]
analyze     10 5.0e2
puts "Finished with elastic gravity analysis..."

# update materials to consider plastic behavior
for {set k 1} {$k <= $numLayers} {incr k} {
    updateMaterialStage -material $k -stage 1
}

# plastic gravity loading
analyze     40 5.0e-2
puts "Finished with plastic gravity analysis..."

#-----------------------------------------------------------------------------------------
#  11. UPDATE ELEMENT PERMEABILITY VALUES FOR POST-GRAVITY ANALYSIS
#-----------------------------------------------------------------------------------------
# if excess pore pressure generation is not allowed (i.e., allowPWP = No),
# permeabilites are left high for dynamic analysis

if {$allowPWP == Yes} {

    # choose base number for parameter IDs which is higer than other tags used in analysis
    set ctr 10000.0
    # loop over elements to define parameter IDs
    for {set i 1} {$i<=$nElemT} {incr i 1} {
       parameter [expr int($ctr+1.0)] element $i vPerm
       parameter [expr int($ctr+2.0)] element $i hPerm
       set ctr [expr $ctr+2.0]
    }


    # update permeability parameters for each element using parameter IDs
    set ctr 10000.0
    for {set j 1} {$j <= $nElemT} {incr j 1} {

     set lowerBound 0.0
     for {set i 0} {$i <= $numLayers} {incr i 1} {

         if {$j <= $layerTopEleNum($i) && $j > $layerTopEleNum([expr $i - 1])} {
            updateParameter [expr int($ctr+1.0)] $vPerm($i)
            updateParameter [expr int($ctr+2.0)] $hPerm($i)
            puts "$j  updateParameter [expr int($ctr+1.0)] $vPerm($i)"

            }
            set lowerBound $layerBound($i)
        }
    set ctr [expr $ctr+2.0]
    }
    puts "Finished updating permeabilities for dynamic analysis..."
}
#-----------------------------------------------------------------------------------------
#  12. CREATE POST-GRAVITY RECORDERS
#-----------------------------------------------------------------------------------------

# reset time and analysis
setTime 0.0
wipeAnalysis
remove recorders

# recorder time step
set recDT  [expr 10*$motionDT]

# # record nodal displacment, acceleration, and porepressure
# record horizontal acceleration at the top node
eval "recorder Node -file $output_dir/out.txt -dT $dT -node $nNodeT -dof 1 accel"
puts "Finished creating all recorders..."

#-----------------------------------------------------------------------------------------
#  13. DYNAMIC ANALYSIS
#-----------------------------------------------------------------------------------------

model BasicBuilder -ndm 2 -ndf 3

# define constant scaling factor for applied velocity
set cFactor [expr $colArea*$dashpotCoeff]

# define velocity time history file
set velocityFile $gMotion


# timeseries object for force history
set mSeries "Path -dt $motionDT -filePath $velocityFile -factor $cFactor"

# loading object
pattern Plain 10 $mSeries {
    load 1  1.0 0.0 0.0
}
puts "Dynamic loading created..."

# For "test" change the last digit to 1 or 2 for debugging

constraints Penalty 1.e16 1.e16
test        NormDispIncr 1.0e-5 35 2
algorithm   KrylovNewton
numberer    RCM
system      ProfileSPD
integrator  Newmark $gamma $beta
rayleigh    $a0 $a1 0.0 0.0
analysis    Transient

# perform analysis with timestep reduction loop
set ok [analyze $nSteps  $dT]

# if analysis fails, reduce timestep and continue with analysis
if {$ok != 0} {
    puts "did not converge, reducing time step"
    set curTime  [getTime]
    set mTime $curTime
    puts "curTime: $curTime"
    set curStep  [expr $curTime/$dT]
    puts "curStep: $curStep"
    set rStep  [expr ($nSteps-$curStep)*2.0]
    set remStep  [expr int(($nSteps-$curStep)*2.0)]
    puts "remStep: $remStep"
    set dT       [expr $dT/2.0]
    puts "dT: $dT"

    set ok [analyze  $remStep  $dT]

    # if analysis fails again, reduce timestep and continue with analysis
    if {$ok != 0} {
        puts "did not converge, reducing time step"
        set curTime  [getTime]
        puts "curTime: $curTime"
        set curStep  [expr ($curTime-$mTime)/$dT]
        puts "curStep: $curStep"
        set remStep  [expr int(($rStep-$curStep)*2.0)]
        puts "remStep: $remStep"
        set dT       [expr $dT/2.0]
        puts "dT: $dT"

        analyze  $remStep  $dT
    }
}
set endT    [clock seconds]
puts "Finished with dynamic analysis..."
puts "Analysis execution time: [expr $endT-$startT] seconds"

wipe
