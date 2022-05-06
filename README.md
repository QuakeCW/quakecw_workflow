# quakecw_workflow
CWNU Earthquake Research Group's Adaptation of QuakeCoRE NZ workflow

Korean Ground Motion Simulation @ Nurion

배성은(University of Canterbury, QuakeCoRE 소프트웨어 팀장 / 창원대학교 BP Fellow)

# 시뮬레이션

이 문서를 따르기 전, Preparation.md 페이지를 참조하고 미리 세팅을 해두도록 한다.

누리온에 로그인하고, act_env 명령어로 가상환경을 실행시킨다.
```
(!522) $ ssh nurion2
Last login: Wed May  4 18:43:35 2022 from 116.120.40.87
================ KISTI 5th NURION System ====================
 * Any unauthorized attempts to use/access the system can be
   investigated and prosecuted by the related Act
   (THE PROTECTION OF INFORMATION AND COMMUNICATIONS INFRASTRUCTURE)

 ....
Filesystem       KBytes        Quota      Files      Quota
------------------------------------------------------------
   /home01       41.24G          64G     140010     200000
  /scratch       56.46T         100T    1665342    2000000
============================================================

x2319a02@login02:~> act_env

 	'gcc/8.3.0' supports the following modules

	{MPI}
	'mvapich2/2.3.1' 'mvapich2/2.3.6' 'openmpi/3.1.0'

	{cpu_types}
	'craype-mic-knl' 'craype-x86-skylake'

	{libraries}
	'CDO/1.8.2' 'hdf4/4.2.13' 'hdf5/1.10.2' 'lapack/3.7.0' 'libxc/4.0.0' 'libxc/4.3.4' 'NCO/4.7.4' 'NCO/4.9.2' 'ncl/6.5.0' 'ncview/2.1.7' 'netcdf/4.6.1'

(python3_nurion) x2319a02@login02:~>
```


최신 버전 소프트웨어로 업데이트한다.

```
cd $QUAKECW
git pull

cd $gmsim
cd workflow
git pull
(
만약 처음이라면, 이 명령어도 실행시켜준다
git checkout quakecw_changes

만약 문제가 있으면
git reset --hard를 먼저 실행시키고, 다시 위의 git checkout을 시도
)

cd ../qcore
git pull

```

$QUAKECW 디렉토리로 옮겨간다.

```
(python3_nurion) x2319a02@login02:~> cd $QUAKECW
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow>
```


# 인풋 모델 만들기

이 예제에서 포항지진을 시뮬레이션해보도록 한다.

$QUAKECW 디렉토리 아래에 RunFolder 디렉토리, 그리고 그 아래에 Pohang 디렉토리를 하나 만들자.

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow> mkdir RunFolder
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow> cd RunFolder
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder> mkdir Pohang
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder> cd Pohang
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang>
```


## 단층 모델 만들기
Source 디렉토리의 `source.yaml`을 수정하거나 복사본을 만들어서 사용하도록 한다. 추후 알아보기 편하도록 적절한 이름을 선택해 저장해두도록 하자.

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> cp $QUAKECW/Source/source.yaml ./source_Pohang.yaml

```
이 파일을 열어보면 단층의 특성에 관련된 내용들이 있다.

```

(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> cat source_Pohang.yaml
TYPE: 2
FAULT: Pohang
# latitude (float)
LAT: 36.109
# longitude (float)
LON: 129.366
# depth (float)
DEPTH: 7
# magnitude (float)
MAG: 5.4
# strike (int)
STK: 230
# dip (int)
DIP: 69
# rake (int)
RAK: 152
# rupture timestep
DT: 0.01
VELOCITY_MODEL: "$QUAKECW/Source/kr_gb_kim2011_modified.1d" <====== 수정 필요
SOURCE_DATA_DIR: "$QUAKCW/RunFolder/Pohang/Source" <====== 수정 필요
```

.yaml파일내의 $QUAKECW와 같은 변수를 인식하지 못하기 때문에, 실제 경로를 집어넣어줘야 한다. 각 사용자마다 $QUAKECW값이 다르므로, 아래 명령어를 사용해서 출력된 값을 복사/붙여넣기하도록 하겠다.

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> echo $QUAKECW
/scratch/x2319a02/users/x2319a02/quakecw_workflow
```
nano를 사용해 source_Pohang.yaml 제일 아래 두줄의 $QUAKECW 부분을 붙여넣기로 수정해준 다음 저장.

수정 후 
```
VELOCITY_MODEL: "/scratch/x2319a02/users/x2319a02/quakecw_workflow/VM/kr_gb_kim2011_modified.1d"
SOURCE_DATA_DIR: "/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Source"
```

아래 명령어를 실행하면 단층 모델이 생성되어 `SOURCE_DATA_DIR`에 위치하게 됨

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/quakecw_workflow/Source> python $QUAKECW/Source/make_source.py source_Pohang.yaml

Executing createSRF.py
2022-05-04 20:12:15,905 - Creating SRF with command: /home01/x2319a02/gmsim/opt/nurion/hybrid_sim_tools/current/genslip_v3.3 read_erf=0 write_srf=1 read_gsf=1 write_gsf=0 infile=Srf/Pohang.gsf mag=5.400000 nx=41 ny=41 ns=1 nh=1 seed=103245 velfile=/scratch/x2319a02/users/x2319a02/quakecw_workflow/VM/kr_gb_kim2011_modified.1d shypo=0.000000 dhypo=2.036901 dt=0.010000 plane_header=1 srf_version=1.0 rvfrac=0.8 alpha_rough=0.01 slip_sigma=0.85
Plotting SRF as square plot...
Plotting SRF as map plot...

mag= 5.40 median mag= 5.22 nslip= 1 nhypo= 1
nx= 41 ny= 41 dx=     0.0994 dy=     0.0994
  0:   129.37172    36.10345 41 41     4.0738     4.0738 230.0 69.0     5.0984
****    16.5000	   16.5000
ratio (negative slip)/(positive slip)= 0.052228
mom=   1.41254e+24 avgslip= 26 maxslip= 78
orig_sigma= 0.264089 ... new_sigma= 0.710031
rt_scalefac= 6.097533
ravg=   1.00000e+00 rmed=   9.99530e-01 rmin=   4.67114e-01 rmax=   1.53759e+00
target_dx= 2.000000 actual dx= 2.035000
target_dy= 2.000000 actual dy= 2.035000
seg= 0
nstk= 41 nx= 2 nxdiv= 2 nxsum= 41
ndip= 41 ny= 2 nydiv= 2 nysum= 41
/home01/x2319a02/gmsim/Environments/v211213/virt_envs/python3_nurion/lib/python3.7/site-packages/shapely/ops.py:42: ShapelyDeprecationWarning: Iteration over multi-part geometries is deprecated and will be removed in Shapely 2.0. Use the `geoms` property to access the constituent parts of a multi-part geometry.
  source = iter(source)
WARNING:root:maximum allowed iterations reached while optimizing the alpha parameter

```
위와 같은 내용이 출력되었다면 성공적으로 단층 모델이 만들어졌다. 
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> cd Source
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Source> tree
.
 |-__pycache__
 | |-srf_config.cpython-37.pyc
 | |-setSrfParams.cpython-37.pyc
 |-Stoch
 | |-Pohang.stoch
 |-setSrfParams.py
 |-Srf
 | |-Pohang.gsf
 | |-Pohang_square.png
 | |-Pohang.srf
 | |-Pohang.info
 | |-Pohang_map.png
 | |-Pohang.SEED
 |-srf_config.py
 |-createSRF.py
 |-cnrs.txt
 |-createSRF_log.txt

```


## 속도 모델 만들기


### 준비

NZVM code에서 부산 분지 모델이 추가된 버전의 바이너리 위치는  

```
/home01/x2319a02/VM_KVM/Velocity-Model-Viz/Velocity-Model/NZVM (2021년 Oct 4 build) (To do: github 에서 maintain)
```


$QUAKE/VM/vm_params.yaml 을 적절히 수정해서 사용 [1]

```
python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> cat $QUAKECW/VM/vm_params.yaml
mag: 5.5
centroidDepth: 4.05399
MODEL_LAT: 35.5755
MODEL_LON: 128.9569
MODEL_ROT: 0.0
hh: 0.1
min_vs: 0.2
model_version: KVM_21p6
topo_type: BULLDOZED
output_directory: output
extracted_slice_parameters_directory: SliceParametersNZ/SliceParametersExtracted.txt
code: rt
extent_x: 250
extent_y: 400
extent_zmax: 40
extent_zmin: 0.0
sim_duration: 60
flo: 1.0
nx: 2500
ny: 4000
nz: 400
sufx: _rt01-h0.100
GRIDFILE: ./gridfile_rt01-h0.100
GRIDOUT: ./gridout_rt01-h0.100
MODEL_COORDS: ./model_coords_rt01-h0.100
MODEL_PARAMS: ./model_params_rt01-h0.100
MODEL_BOUNDS: ./model_bounds_rt01-h0.100
```
[1] 
* model_version: KVM_21p6은 부산 분지 모델이 들어간 버전임을 의미함. 
* hh: 0.1은 그리드 간격이 100m를 의미함. 
* extent_x = hh \* nx
* extent_y = hh \* ny 
* (extent_zmax-extent_zmin)=hh\*nz 
* flo = 0.1 / hh 의 상관 관계가 있으며, 따라서 hh=0.1 --> flo: 1.0, hh=0.4 --> flo: 0.25 


### 실행  

간단한 예를 보여주기 위해 제공된 vm_params_1000.yaml을 이용하도록 하겠다. 이 속도 모델을 Busan1000이라 부르기로 함. 


```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> python $QUAKECW/VM/make_vm.py $QUAKECW/VM/vm_params_1000.yaml Busan1000 --outdir ./VM --ncores 16 --wallclock 2

Created: /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/VM
Loaded: /scratch/x2319a02/users/x2319a02/quakecw_workflow/VM/vm_params_1000.yaml
Copied vm_params_1000.yaml to /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/VM
/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/tmpduik7ld_.template
Generated: /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/VM/make_vm.pbs
Submitted: qsub -V /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/VM/make_vm.pbs
10082371.pbs 
```

ncores은 노드 전체의 경우 68, wallclock 은 남한 대부분을 커버하는 100m 모델의 경우 15시간 정도 세팅이 적당하여 디폴트값으로 정해져 있으나 작은 사이즈의 예시로 사용하기 위해 옵션의 사용법을 제시하였다. 



### 진행상황 체크

속도 모델 생성 명령어를 실행할 때 `outdir`로 현재 디렉토리의 `VM`을 설정하였다.
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> cd VM
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/VM> ls
make_vm.pbs  vm_params.yaml
```

vm_params_1000.yaml의 복사본, 그리고 제출한 PBS스크립트이 위치해있다. 속도 모델이 생성되면 또한 이 곳에 위치하게 될 것이다.


현재 진행 상활을 체크해 보도록 한다.
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/VM> qstat -u $USER

pbs:
                                                                 Req'd  Req'd   Elap
Job ID               Username Queue    Jobname    SessID NDS TSK Memory Time  S Time
-------------------- -------- -------- ---------- ------ --- --- ------ ----- - -----
10082371.pbs         x2319a02 normal   make_vm       --    1  68    --  02:00 Q   --

```
현재 이 job은 제출되어 대기중인 상태로 (Queued) 정상적으로 진행되면 Q->R (running) -> E (ending) 순으로 진행되는 과정을 볼수 있다. 총 2시간을 요청하였으며, 전체 코어가 68개인 노드에서 계산 될 예정이다 (다만 요청은 위에서 ncores =16으로 하였음) 

`R`로 진행되고 나면 Job ID를 참고하여, 현재 $HOME 디렉토리에서 임시로 쓰여지고 있는 아웃풋 파일의 업데이트 상황을 모니터할 수 있다
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/VM> tail -f $HOME/pbs.10082371.pbs.x8z/10082371.pbs.OU
```
아래와 같은 내용을 볼 수 있을 것이다.
```
Completed loading of global surfaces.
Loading basin data.
Loading KVM_21p6 perturbation files.
Completed Loading of perturbation files.
All basin surfaces loaded.
All basin boundaries loaded.
All basin sub model data loaded.
Completed loading basin data.
All global data loaded.
Generating velocity model
3% complete.
```

### 생성파일 체크

위에서 서브밋한 pbs스크립트는 16코어를 이용해 NZVM을 실행시켜 \*.p, \*.s, \*.d 파일을 생성시키고, gen_coords.py를 불러 model_params, model_bounds, model_params 등과 같은 좌표 파일들을 도메인에 맞게 생성해낸다. 아래와 같은 파일들이 최종적으로 디렉토리에 상주하게 됨

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/VM> tree
.
 |-nzvm.cfg
 |-vm_params2vm_log.txt
 |-vs3dfile.s
 |-VeloModCorners.txt
 |-rho3dfile.d
 |-vm_params2vm_Busan1000_log.txt
 |-model_params_rt01-h1.0
 |-gridfile_rt01-h1.0
 |-vp3dfile.p
 |-make_vm.e10083011
 |-make_vm.o10083011
 |-vm_params.yaml
 |-model_coords_rt01-h1.0
 |-gridout_rt01-h1.0
 |-model_bounds_rt01-h1.0
 |-make_vm.pbs

```

## 관측소 리스트 만들기

관측소 리스트는 속도모델의 범위 안에서 가로 세로 2km마다의 간격으로 가상 관측소를 만들고, 실제로 존재하는 관측소 위치를 추가하여 만든다. 

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> python $QUAKECW/Stations/make_stations.py VM/vm_params.yaml --real_stats $QUAKECW/Stations/realstations_20220420.ll --outdir Stations --name Busan_2km
created temp dir VM/tmp4x3shtd5
input .ll file: Stations/Busan_2km.ll
output .v30 file: Stations/Busan_2km.vs30
```

이 스크립트의 첫 인풋 `vm_params.yaml`의 패스는 필수이다. 옵션으로 실재 관측소 위치 파일을 `--real_stats`로 추가할 수 있으며, 결과값 파일들이 저장될 디렉토리를 `--outdir`로 지정할 수 있다. (미지정시 현재 위치). 결과 파일이름을 `--name`으로 설정할 수 있다. `Busan_2km.ll`과 `Busan_2km.vs30`가 각각 생성된다. 미지정시 `stats.ll`, `stats.vs30`이 됨.

실재 관측소 위치 파일은 `realstations_20220420.ll`으로 기본 제공되며, 그 포맷은 아래와 같다.
```
127.8790 35.4131 SACA
127.8946 34.9832 GMNA
127.9188 35.6140 KCH2
127.9261 34.8167 NAHA
127.9441 36.4413 HWSA
128.0402 35.1642 JINA
...
(총 121)

```

## 시뮬레이션 인스톨

단층 모델과 속도 모델이 준비되어 있다고 가정하고 시뮬레이션 실행법에 대해 기술하겠음. 단층 모델이나 속도 모델이 준비 되지 않았다면, 위에서 서술한 단계를 따라 이들을 우선 생성하도록 할것.

KISTI 누리온 5호기에서 x2319a02계정으로 실행할 것임. 

$QUAKECW의 gmsim.yaml을 복사해서 수정해 사용하자.

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> cp $QUAKECW/gmsim.yaml gmsim_Pohang.yaml
```

gmsim_Pohang.yaml에 $HOME, $QUAKECW 변수들을 echo 명령어로 실제 경로를 파악하여 수정, 저장한다.

```
workflow: $HOME/gmsim/Environments/v211213/workflow
sim_root_dir: $QUAKECW/RunFolder/Pohang
fault_name: Pohang
source_data: $QUAKECW/RunFolder/Pohang/Source
copy_source_data: False
vm_data: $QUAKECW/RunFolder/Pohang/VM
copy_vm_data: False
gmsim_template: $HOME/gmsim/Environments/v211213/workflow/workflow/calculation/gmsim_templates/Pohang_22.03.13.3
stat_file: $QUAKECW/RunFolder/Pohang/Stations/Busan_2km.ll
n_max_retries: 2
```

로그인 어카운트가 x2319a02인 사용자의 경우 아래와 같이 저장한다. 

```
workflow: /home01/x2319a02/gmsim/Environments/v211213/workflow
sim_root_dir: /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang
fault_name: Pohang
source_data: /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Source
copy_source_data: False
vm_data: /scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan_20220324 <-----
copy_vm_data: False
gmsim_template: /home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/calculation/gmsim_templates/Pohang_22.03.13.3
stat_file: /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Stations/Busan_2km.ll
n_max_retries: 2
```
특별히 `vm_data`에 유의할 것. 우리가 위에서 생성한 속도모델은 hh=1.0로 지나치게 단순하여, 기존 시뮬레이션에서 주로 사용하는 hh=0.1 속도모델을 사용하기로 한다. 

각각의 변수들을 설명하자면
1. workflow: slurm_gm_workflow가 인스톨되어 있는 위치
2. sim_root_dir: 시뮬레이션을 실행시키고자 하는 디렉토리 위치
3. fault_name: 시뮬레이션을 실행시킬 이벤트(단층)의 이름
4. source_data: 단층 모델 데이터가 위치한 곳. 
5. copy_source_data: 단층 모델 데이터를 sim_root_dir 속으로 복사해 올 것인지 (True), 심볼릭 링크의 형태로 연결만 할 것인지 (False)
6. vm_data: 속도 모델 데이터가 위치한 곳
7. copy_vm_data: 속도 모델 데이터를 sim_root_dir 속으로 복사해 올 것인지 (True), 심볼릭 링크의 형태로 연결만 할 것인지 (False)
8. gmsim_template: 시뮬레이션의 상세 사항 (HF 버전, sdrop, path_dur, kappa, IM pSA주기, 1차원 속도모델 등) 을 지정해둔 템플릿이 저장된 디렉토리
9. stat_file: 관측소 리스트
10. n_max_retries: 계산 실패시 재시도 회수 최대값


우선 누리온의 로그인 노드가 접속 중 활동이 없으면 네트워크 연결을 끊어버리는 경우가 많아 타임아웃 무제한으로 만들고 screen 세션안에서 실행하는 것을 권장한다.
다음 명령어를 실행하셔 screen 안으로 들어간다.

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> export TMOUT=
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> screen
```

가상 환경을 활성화 해준다. (screen 세션이 시작될 때 기존에 있었던 가상 환경이 리셋됨)
```
x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> act_env
```

아래와 같은 에러가 자주 목격되는데, 무시해도 무방함.

```
x2319a02@login04:/scratch/x2319a02/gmsim/RunFolder/Busan20211214> activate_env /home01/x2319a02/gmsim/Environments/v211213/
cray-impi/1.1.4(154):ERROR:102: Tcl command execution failed: set CompilerVer \[ glob -tails -directory ${VERSION_PREFIX}/${Compiler} -type d \* ]
cray-impi/1.1.4(154):ERROR:102: Tcl command execution failed: set CompilerVer \[ glob -tails -directory ${VERSION_PREFIX}/${Compiler} -type d \* ]
cray-impi/1.1.4(154):ERROR:102: Tcl command execution failed: set CompilerVer \[ glob -tails -directory ${VERSION_PREFIX}/${Compiler} -type d \* ]   

'craype-x86-skylake' dependent modulefiles were removed
```


스크립트를 실행시켜 시뮬레이션을 설치

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> python $QUAKECW/
install_gmsim.py gmsim_Pohang.yaml
```


실행 장면


```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> python $QUAKECW/install_gmsim.py gmsim_Pohang.yaml
Pohang 1r

python /home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/automation/install_scripts/install_cybershake.py /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/fault_list.txt /home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/calculation/gmsim_templates/Pohang_22.03.13.3 --stat_file_path /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Stations/Busan_2km.ll --keep_dup_station
Version path: /home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/calculation/gmsim_templates/Pohang_22.03.13.3
2022-05-05 01:55:39,880 - Installing /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Data/Sources/Pohang/Srf/Pohang.srf
****************************************************************************************************
2022-05-05 01:55:39,895 - installing bb
****************************************************************************************************
2022-05-05 01:55:39,896 -                                      EMOD3D HF/BB Preparation Ver.slurm
****************************************************************************************************
2022-05-05 01:55:39,896 - installing bb finished
2022-05-05 01:55:40,095 - /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Stations/Busan_2km.ll
2022-05-05 01:55:40,095 - From: /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Stations/Busan_2km.ll. To: /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Runs/Pohang/fd_rt01-h0.100.statcords, /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Runs/Pohang/fd_rt01-h0.100.ll


================================
             Source
================================
/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Data/Sources/Pohang/setSrfParams.py
LAT: 36.109
LON: 129.366
DEPTH: 7
MAG: 5.4
STK: 230
DIP: 69
RAK: 152
DT: 0.01
================================
             VM
================================
/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Data/VMs/Pohang/vm_params.yaml
{'GRIDFILE': './gridfile_rt01-h0.100',
 'GRIDOUT': './gridout_rt01-h0.100',
 'MODEL_BOUNDS': './model_bounds_rt01-h0.100',
 'MODEL_COORDS': './model_coords_rt01-h0.100',
 'MODEL_LAT': 35.753,
 'MODEL_LON': 128.4038,
 'MODEL_PARAMS': './model_params_rt01-h0.100',
 'MODEL_ROT': 0.0,
 'centroidDepth': 4.05399,
 'code': 'rt',
 'extent_x': 325,
 'extent_y': 360,
 'extent_zmax': 68,
 'extent_zmin': 0.0,
 'extracted_slice_parameters_directory': 'SliceParametersNZ/SliceParametersExtracted.txt',
 'flo': 1.0,
 'hh': 0.1,
 'mag': 5.5,
 'min_vs': 0.2,
 'model_version': 'KVM_21p6',
 'nx': 3250,
 'ny': 3600,
 'nz': 680,
 'output_directory': 'output',
 'sim_duration': 90,
 'sufx': '_rt01-h0.100',
 'topo_type': 'BULLDOZED'}
================================
       GMSIM template
================================
/home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/calculation/gmsim_templates/Pohang_22.03.13.3/root_defaults.yaml
{'bb': {'fmidbot': 0.5, 'fmin': 0.2, 'no-lf-amp': True},
 'dt': 0.005,
 'emod3d': {'emod3d_version': '3.0.4'},
 'flo': 1.0,
 'hf': {'dt': 0.005,
        'kappa': 0.016,
        'path_dur': 2,
        'rvfac': 0.5,
        'sdrop': 50,
        'version': '5.4.5.3'},
 'ims': {'component': ['geom'],
         'extended_period': False,
         'pSA_periods': [0.01,
                         0.02,
                         0.03,
                         0.04,
                         0.05,
                         0.075,
                         0.1,
                         0.12,
                         0.15,
                         0.17,
                         0.2,
                         0.25,
                         0.3,
                         0.4,
                         0.5,
                         0.6,
                         0.7,
                         0.75,
                         0.8,
                         0.9,
                         1.0,
                         1.25,
                         1.5,
                         2.0,
                         2.5,
                         3.0,
                         4.0,
                         5.0,
                         6.0,
                         7.5,
                         10.0]},
 'v_1d_mod': 'kr_gb_kim2011_modified.1d'}
Simulation installed at /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang
Run with : $QUAKECW/run_gmsim.sh /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/gmsim_Pohang.yaml
 
```


참고: 처음 실행할 때 아래와 같은 에러가 발생하며 중단될 수 있음.
```
Error: VM Pohang failed 
VM extents not contained within NZVM DEM: 130.36976143733443, 37.36407162688109
VM extents not contained within NZVM DEM: 127.54403856266556, 37.36407162688109
VM extents not contained within NZVM DEM: 127.60603497578211, 33.77116521934643
VM extents not contained within NZVM DEM: 130.3077650242179, 33.77116521934643 
VM extents not contained within NZVM DEM: 127.607221, 33.771972
VM extents not contained within NZVM DEM: 127.545307, 37.363293
VM extents not contained within NZVM DEM: 130.368482, 37.363293
VM extents not contained within NZVM DEM: 130.306569, 33.771972
```
`$gmsim/workflow/workflow/automation/install_scripts/install_cybershake_fault.py` 의 라인 173에서 시뮬레이션 위치가 뉴질랜드 영토인지 체크하는 부분 때문에 에러가 발생한 것으로 코드를 수정하여 무시하도록 하면 됨.


시뮬레이션 실행 디렉토리에 인스톨이 끝나면 아래와 같은 디렉토리 구조를 가지게 됨. (Source, VM, Stations를 제외한 모습)

```
.

 |-slurm_mgmt.db
 |-Stations
 | |-Busan_2km.vs30
 | |-Busan_2km.ll
 |-source_Pohang.yaml
 |-task_config.yaml
 |-master_log_20220504_231859.txt
 |-queue_monitor_log_20220504_231859.txt
 |-wrapper_log_20220504_231859.txt
 |-install_quakecw_log_20220504_233017.txt
 |-install_cybershake_log_20220504_233137.txt
 |-main_auto_submit_log_20220504_231859.txt
 |-Data
 | |-Sources
 | | |-Pohang
 | |-VMs
 | | |-Pohang
 |-gmsim_Pohang.yaml
 |-fault_list.txt
 |-scheduler_log_20220504_231859.txt
 |-Runs
 | |-Pohang
 | | |-Pohang
 | | | |-LF
 | | | |-HF
 | | | |-IM_calc
 | | | |-BB
```


## 시뮬레이션 실행

Cybershake 워크플로우를 인스톨하면 자동화 스케쥴러를 사용할 수 있다. 이 스케쥴러는 로그인 노드에서 상주하며 실행 중인 job을 모니터하고, 의존 관계에 있는 job들이 성공적으로 완료되면 그 다음 단계의 job을 자동으로 submit하는 기능이 있다.

quakecw_workflow 디렉토리 안으로 들어가거나, path를 적절히 보태어서 아래 명령을 실행한다.

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang> $QUAKECW/run_gmsim.sh /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/gmsim_Pohang.yaml
```

스크립트가 실행되면서 아래와 같은 아웃풋이 출력된다.
```
sim_root_dir: /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang
workflow: /home01/x2319a02/gmsim/Environments/v211213/workflow
n_max_retries: 2
python /home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/automation/execution_scripts/run_cybershake.py /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang x2319a02 /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/task_config.yaml --n_max_retries 2
2022-05-05 01:56:24,909 - MainThread - Logger file added
2022-05-05 01:56:24,919 - MainThread - Master script will run [<ProcessType.EMOD3D: 1>, <ProcessType.HF: 4>, <ProcessType.BB: 5>, <ProcessType.IM_calculation: 6>, <ProcessType.merge_ts: 2>, <ProcessType.plot_ts: 3>, <ProcessType.IM_plot: 7>]
2022-05-05 01:56:24,923 - MainThread - Created queue_monitor thread
2022-05-05 01:56:24,923 - MainThread - Created main auto_submit thread
2022-05-05 01:56:24,924 - MainThread - Started main auto_submit thread
2022-05-05 01:56:24,924 - queue monitor - Running queue-monitor, exit with Ctrl-C.
2022-05-05 01:56:24,925 - MainThread - Started queue_monitor thread
2022-05-05 01:56:24,941 - main auto submit - Loaded root params file: /scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Runs/root_params.yaml
2022-05-05 01:56:25,878 - main auto submit - Number of runnable tasks: 2
2022-05-05 01:56:25,879 - main auto submit - Tasks to run this iteration: Pohang-EMOD3D, Pohang-HF
2022-05-05 01:56:26,147 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-05-05 01:56:26,151 - queue monitor - No entries in the mgmt db queue.
submit_time not in proc_Data.keys(),value 2022-05-05_01:56:25

submit_time not in proc_Data.keys(),value 2022-05-05_01:56:28

2022-05-05 01:56:31,917 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-05-05 01:56:31,922 - queue monitor - Updating 2 mgmt db tasks.
2022-05-05 01:56:31,923 - queue monitor - Acquiring db connection.
2022-05-05 01:56:37,527 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-05-05 01:56:37,529 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10170379-queued, Pohang-HF-10170380-queued
2022-05-05 01:56:37,531 - queue monitor - No entries in the mgmt db queue.
2022-05-05 01:56:42,848 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-05-05 01:56:42,850 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10170379-queued, Pohang-HF-10170380-queued
2022-05-05 01:56:42,852 - queue monitor - No entries in the mgmt db queue.
2022-05-05 01:56:48,334 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-05-05 01:56:48,336 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10170379-queued, Pohang-HF-10170380-queued
2022-05-05 01:56:48,338 - queue monitor - No entries in the mgmt db queue.
2022-05-05 01:56:53,695 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-05-05 01:56:53,696 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10170379-queued, Pohang-HF-10170380-queued
2022-05-05 01:56:53,698 - queue monitor - No entries in the mgmt db queue.
2022-05-05 01:56:59,031 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-05-05 01:56:59,033 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10170379-queued, Pohang-HF-10170380-queued
2022-05-05 01:56:59,035 - queue monitor - No entries in the mgmt db queue.
....
2022-05-05 02:33:37,033 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10170379-running, Pohang-HF-10170380-running
2022-05-05 02:33:37,035 - queue monitor - No entries in the mgmt db queue.
...

```


마지막 부분들은 Pohang의 EMOD3D와 HF job이 Queue에 추가되어 실행을 기다리다 (queued) 실행중 (running) 상태로 넘어간 모습을 보여줌

Ctrl+a d로 스크린을 detach한뒤 (혹은 새로 ssh 연결한 다음) qstat으로 현재 상태를 알아볼 수 있다.
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/Pohang_20220417> qstat -u $USER

pbs:
                                                                 Req'd  Req'd   Elap
Job ID               Username Queue    Jobname    SessID NDS TSK Memory Time  S Time
-------------------- -------- -------- ---------- ------ --- --- ------ ----- - -----
10067167.pbs         x2319a02 normal   emod3d.Po*    --   26 17*    --  09:06 Q   --
10067168.pbs         x2319a02 normal   hf.Pohang   14394   1  68    --  00:30 R 00:01
```


`-u $USER`는 누리온 슈퍼컴퓨터에 존재하는 모든 작업 중에서 현재 사용자가 제출한 것들만 출력하라는 옵션이다. 현재 두개의 job들, 10067167.pbs, 10067168.pbs가 PBS스케쥴러에 있음을 보여주는데, S 항목의 Q는 이 작업이 추가(Queued)되어 실행 대기중임을, R는 현재 이 실행중인 (Running) 상태임을 의미한다. 정상적인 상황이라면 Q->R->E  (Queued -> Running -> Ending) 순으로 진행된다.


`run_gmsim.sh`은 사실 `run_cybershake.py`을 실행하기 쉽도록 가공한 스크립트이다. Cybershake 실행할 때 제공한 task_config.yaml에서 요청한 바에 따라 워크플로우는 인스톨된 단층모델들, Pohang 각 1개씩의 realisation의 저주파(LF, 주로 EMOD3D로 불리움), 고주파(HF), BB (broadband = LF+HF) 등의 job을 누리온에 자동으로 submit하고 각 job의 진행상황을 모니터함과 동시에,의존도가 충족되면 다음 단계의 job을 다시 submit하고 모니터링한다.

job을 서브밋할 때, 필요한 리소스와 wallclock 같은 변수도 자동으로 예상하여 그 값을 사용하는데, 만약 작업시간이 예상을 초과하여 계산이 중단되면, 예상시간을 늘여서 다시 서브밋하도록 제작되어 있음. (2차 시도는 시간 2배, 3차 시도는 시간 3배..)

위와 같은 이유로 시뮬레이션이 아직 안정화되지 못한 경우, 다양한 이유로 job이 실패할 수 있으나 그럴 때마다 예상시간을 늘이며 다시 서브밋된다면 누리온 계정의 allocation을 낭비하게 될 수도 있음. 따라서 이 워크플로우는 시뮬레이션이 이미 안정화 단계에 있을 때 사용하는 것을 권장함.

한편, `run_gmsim.sh`는 최고 2번의 시도를 하도록 되어 있으며, 2차 시도 끝에도 계산이 제대로 끝나지 못했다면 다음 방법을 사용할 수 있다.


### 재시도

만약 정해진 횟수 내에 어떤 이유로 계산이 성공적으로 완료되지 않았다면, 그 원인을 수정한 다음, `gmsim.yaml`의 `n_max_retries`값을 수정하고 다시 `run_gmsim.sh`을 실행할 수 있다. 
  
예시) BB를 2회 시도하였으나, .vs30 파일이 지정된 위치에 있지 않은 이유로 BB가 종료되지 않은 상태에서 계산이 중단되었다면, 원인을 해결하고(예: .vs30 파일을 지정된 위치로 복사), `gmsim.yaml`의 `n_max_retries`값을 3 이상의 값으로 수정한 다음, 다시 `run_gmsim.sh`을 실행하면 된다.


### job 진행 상태를 파악하기


#### 전체 상황
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/Runs/Pohang> python $QUAKECW/check_status.py gmsim_Pohang.yaml
                 run_name |         process |     status |   job-id |        last_modified
_________________________________________________________________________________________________
                   Pohang |        merge_ts |    created |     None |  2022-04-17 09:27:24
                   Pohang |         plot_ts |    created |     None |  2022-04-17 09:27:24
                   Pohang |              BB |    created |     None |  2022-04-17 09:27:24
                   Pohang |  IM_calculation |    created |     None |  2022-04-17 09:27:24
                   Pohang |         IM_plot |    created |     None |  2022-04-17 09:27:24
                   Pohang |          EMOD3D |     queued | 10067167 |  2022-04-18 08:13:52
                   Pohang |              HF |  completed | 10067168 |  2022-04-18 08:25:26
```
모두 완전하게 끝났다면 아래와 같은 출력물을 볼 수 있다

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/Runs/Pohang> python $QUAKECW/check_status.py gmsim_Pohang.yaml
                 run_name |         process |     status |   job-id |        last_modified
_________________________________________________________________________________________________
                   Pohang |          EMOD3D |  completed | 10067167 |  2022-04-18 17:38:53
                   Pohang |              HF |  completed | 10067168 |  2022-04-18 08:25:26
                   Pohang |        merge_ts |  completed | 10068634 |  2022-04-18 18:06:36
                   Pohang |              BB |  completed | 10068635 |  2022-04-18 18:08:15
                   Pohang |         plot_ts |  completed | 10068663 |  2022-04-18 18:22:04
                   Pohang |  IM_calculation |  completed | 10068665 |  2022-04-18 20:20:34
                   Pohang |         IM_plot |  completed | 10069305 |  2022-04-18 20:39:50
```


각각의 job의 현재 상태를 파악하고 싶다면 screen을 잠시 빠져나오거나 (detach, Ctrl+a d), 다른 터미널에서 아래와 같은 방법을 사용할 수 있다.


#### LF (EMOD3D)

LF/Rlog디렉토리에 \*.rlog파일이 업데이트 되는 과정을 관찰하면 됨

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Runs/Pohang/Pohang/LF/Rlog/tail -f Pohang-00000.rlog

...
    17300     28.43  2578.12   1.00      88.78   0.98         13692.   0.99
    17400     24.96  2578.12   1.00      82.44   1.00         13774.   0.99
    17500     17.67  2578.12   1.00      75.25   1.00         13849.   0.99
...
    
```
현재까지 timestep 17500까지 계산했음을 보여준다.  LF/e3d.par의 nt값을 확인하면 timestep이 18200에 도달할 때까지 계산이 지속되어야 함을 알수 있음.

계산이 끝났다면 rlog파일의 끝에서 아래와 같은 문구를 볼 수 있다.
```
*** usage totals:     Mbytes Transfered    System CPU      User CPU   %Real
                              469052.00          268.        14130.    0.99
PROGRAM emod3d-mpi IS FINISHED
```


#### HF

HF/Acc에 HF.bin, HF.log 파일 사이즈가 증가하는 것이 관찰되면 정상적으로 작동하고 있다고 짐작할 수 있음

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/users/x2319a02/quakecw_workflow/RunFolder/Pohang/Runs/Pohang/Pohang/HF/Acc> ls -ltr
total 6226180
-rw-rw-r-- 1 x2319a02 rd0624          8 Mar 28 09:17 SEED
-rw-rw-r-- 1 x2319a02 rd0624 6358882976 Mar 28 09:27 HF.bin
-rw-rw-r-- 1 x2319a02 rd0624   16652983 Mar 29 12:54 HF.log
```

계산이 모두 끝나면 LF와 HF 모두 결과값이 원하는 포맷과 일치하는지 간단한 검증 과정을 거친다. 통과하면 Complete로 마크되고 그 다음 단계에 계산할 job이 있다면 (이 경우 BB) submit하게 된다.




# 시각화

누리온 로긴 노드에서 직접 다양한 지도들을 생성할 수 있다.

### IM_plot (업데이트 필요)

IM_Calculation단계를 거쳐야 함.시뮬레이션 디렉토리에서 IM_calc디렉토리에 \*.csv파일이 존재하는 지 확인할 것.

IM Calculation 결과와 관측점의 위도/경도를 매칭해서 xyz파일을 생성해낸다.

IM_calc의 parent 디렉토리 (LF,HF,BB등이 있는 곳)로 가서 아래를 실행시킴

```

FAULT=Pohang
REL=Pohang
python $gmsim/visualization/im/spatialise_im.py IM_calc/${REL}.csv ../fd_rt01-h0.100.ll -o plot
```

위에서 non_uniform_im.xyz파일이 plot이라는 디렉토리에 생성되었을 것임. 아울러 im_order.txt라는 파일도 생겨나는데, 계산된 IM들의 순서가 기록된 파일임.

  
plot 디렉토리에 가서 아래 명령어를 입력. FAULT와 REL을 위처럼 변수로 지정해주면 다른 시뮬레이션 결과값에 대응할 수 있다.  
  

```
cd plot
python $gmsim/visualization/sources/plot_items.py -c ../../../../Data/Sources/${FAULT}/Srf/${REL}.srf --xyz non_uniform_im.xyz -t ${FAULT} --xyz-cpt-label `cat im_order.txt` -f ${FAULT} --xyz-landmask --xyz-cpt hot --xyz-transparency 30 --xyz-grid --xyz-grid-contours --xyz-grid-search 12m --xyz-size 1k --xyz-cpt-invert --xyz-model-params ../../../../Data/VMs/${FAULT}/model_params_rt01-h0.100 -n 4
```
  

### Plot_ts (업데이트 필요)

자동으로 실행되도록 되어 있으나, 수동으로 실행해야 할 경우, 인스톨 시킨 디렉토리로 돌아가서 (Runs와 Data디렉토리를 포함한 곳) 아래를 실행

qsub -v XYTS_PATH=Runs/${FAULT}/${REL}/LF/OutBin/${REL}\_xyts.e3d,SRF_PATH=Data/Sources/${FAULT}/Srf/${REL}.srf,OUTPUT_TS_PATH=Runs/${FAULT}/${REL}/verification/${REL},MGMT_DB_LOC=\`pwd\`,SRF_NAME="${REL}" -V $gmsim/workflow/workflow/automation/org/kisti/plot_ts.pbs


# 관측 데이터

## 관측 데이터 준비 및 가속도->속도 변환
관측데이터들은 `/scratch/x2319a02/gmsim/Busan_Data/Data/Obs`에 보관되어 있다. 출처에 따라 KIGAM, KINS, KMA로 나뉘어져 있으며, 그 밑에 Pohang, Gyeongju등의 이벤트로 나뉘어져 있다.
해당 위치에서 qcore가 요구하는 형태 관측소.{000,090,ver} 포맷으로 전환 (@seokhojeong) 하고, (예)` 171115_Acc_qcore`, 이들을 통합 저장소인 `/scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined`의 해당 이벤트에 위치한 `Obs_Acc`로 복사한다. (예) `/scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined/Pohang/Obs_Acc` 끝으로 convert_acc2vel.py 스크립트를 이용해 속도 데이터로 변환한다.

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined/Pohang> python ../../convert_acc2vel.py

```

## 관측 데이터 IM calc (업데이트 필요)
가속도 데이터에서 Intensity measurement들을 계산해 낼 수 있다.
아래 명령어에서 EVENT를 수정하고 나머지를 복사&붙여넣기하면 됨
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined/Gyeongju> EVENT=Gyeongju python $gmsim/IM_calculation/IM_calculation/scripts/calculate_ims.py Obs_Acc a -o Obs_IM -i $EVENT -r $EVENT -np 40  -t o -c geom -s -p 0.01 0.02 0.03 0.04 0.05 0.075 0.1 0.12 0.15 0.17 0.2 0.25 0.3 0.4 0.5 0.6 0.7 0.75 0.8 0.9 1.0 1.25 1.5 2.0 2.5 3.0 4.0 5.0 6.0 7.5 10.0 

2022-04-22 13:51:11,678 - IM_Calc started
Reading waveforms in: g
2022-04-22 13:51:12,361 - Processing HSB - 2 / 46
2022-04-22 13:51:12,363 - Processing EUSB - 1 / 46
2022-04-22 13:51:12,364 - Processing HCNA - 3 / 46
2022-04-22 13:51:12,365 - Processing JINA - 4 / 46
2022-04-22 13:51:12,366 - Processing YOCB - 5 / 46
2022-04-22 13:51:12,368 - Processing PHA2 - 6 / 46
2022-04-22 13:51:12,368 - Processing HWSB - 7 / 46
2022-04-22 13:51:12,371 - Processing YGN - 8 / 46
2022-04-22 13:51:12,371 - Processing BBK - 9 / 46
2022-04-22 13:51:12,372 - Processing AJD - 10 / 46
2022-04-22 13:51:12,374 - Processing MIYA - 13 / 46
2022-04-22 13:51:12,373 - Processing HAK - 11 / 46
2022-04-22 13:51:12,374 - Processing DOKDO - 12 / 46
2022-04-22 13:51:12,376 - Processing KJM - 14 / 46
2022-04-22 13:51:12,377 - Processing JJB - 15 / 46
2022-04-22 13:51:12,378 - Processing KUJA - 16 / 46
2022-04-22 13:51:12,379 - Processing JRB - 17 / 46
2022-04-22 13:51:12,381 - Processing KRN - 18 / 46
2022-04-22 13:51:12,383 - Processing HDB - 19 / 46
2022-04-22 13:51:12,384 - Processing BGD - 20 / 46
2022-04-22 13:51:12,385 - Processing MUN - 21 / 46
2022-04-22 13:51:12,387 - Processing MAK - 22 / 46
2022-04-22 13:51:12,387 - Processing KSA - 23 / 46
2022-04-22 13:51:12,389 - Processing CGD - 24 / 46
2022-04-22 13:51:12,389 - Processing CHS - 25 / 46
2022-04-22 13:51:12,391 - Processing NPR - 26 / 46
2022-04-22 13:51:12,392 - Processing DAG2 - 27 / 46
2022-04-22 13:51:12,394 - Processing CIGB - 28 / 46
2022-04-22 13:51:12,396 - Processing KCH2 - 29 / 46
2022-04-22 13:51:12,397 - Processing DKJ - 31 / 46
2022-04-22 13:51:12,397 - Processing BRS - 30 / 46
2022-04-22 13:51:12,398 - Processing ADO2 - 32 / 46
2022-04-22 13:51:12,400 - Processing GRE - 33 / 46
2022-04-22 13:51:12,402 - Processing KMC - 34 / 46
2022-04-22 13:51:12,404 - Processing UCN - 35 / 46
2022-04-22 13:51:12,405 - Processing HKU - 36 / 46
2022-04-22 13:51:12,406 - Processing EURB - 37 / 46
2022-04-22 13:51:12,408 - Processing HACA - 38 / 46
2022-04-22 13:51:12,411 - Processing BRN - 39 / 46
2022-04-22 13:51:12,412 - Processing RWD - 40 / 46
2022-04-22 13:51:12,520 - Processing JSB - 41 / 46
2022-04-22 13:51:12,529 - Processing WSN - 42 / 46
2022-04-22 13:51:12,552 - Processing MGB - 43 / 46
2022-04-22 13:51:12,564 - Processing MKL - 44 / 46
2022-04-22 13:51:12,565 - Processing GSU - 45 / 46
2022-04-22 13:51:12,569 - Processing PCH - 46 / 46
100.0% complete. Time taken for this block:  0.99s. Time elapsed:  0.99s. Time remaining:  0.00s. Total time:  0.99s.
Calculations are output to Obs_IM
```

## 관측 데이터와 시뮬레이션 결과값의 비교 (업데이트 필요)
```
mkdir Pohang_waveforms8
cp //scratch/x2319a02/gmsim/quakecw_workflow/analysis/* Pohang_waveforms8
cd Pohang_waveforms8
ln -s /scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined/Pohang/Obs_IM
ln -s /scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined/Pohang/Obs_Acc
ln -s /scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined/Pohang/Obs_Vel

cat RELS.txt (<- edit this)
Pohang_20220422_sdrop20
Pohang_20220422_sdrop50

FAULT=Pohang REL=Pohang ./run_waveforms.sh
FAULT=Pohang REL=Pohang ./run_psa_comparison.sh
FAULT=Pohang REL=Pohang ./collect_im_plots.sh
```


# 참고 문헌:

[Ground motion simulation run manual (20p07) - QuakeCoRE: The Centre for Earthquake Resilience - Confluence (canterbury.ac.nz)](https://wiki.canterbury.ac.nz/pages/viewpage.action?pageId=90538503)

  
 


참고: 데이터 이전 이후 망가진 심볼릭 링크 고치는 법

Old_id=hpc11a02

New_id=x2319a02

라고 가정

Busan\* 이라는 디렉토리 내의 모든 망가진 심볼릭 링크를 찾아서 고치기를 원한다면, 아래 명령어를 적절히 수정하여 실행하면 됨.

find Busan\* -type l|xargs -I{} ls -al {} |grep**x2319a02** |awk '{print $9" "$11}' >links.txt

cat links.txt | while read line; do word=( $line ); dest=${word\[0]}; old_link=${word\[1]}; new_link=${word\[1]}; new_link=${new_link/**hpc11a02**/**x2319a02**}; echo $new_link; rm done

  


특정 text를 포함하는 모든 파일들을 찾아 그 속의 text를 새로운 것으로 바꾸는 법

(python3_nurion) x2319a02@login01:~/gmsim/Environments/v211213> grep -r hpc11a02 \* |grep -v pyc |grep -v Binary |cut -d: -f1 |xargs -I {} sed -i 's/hpc11a02/x2319a02/g' {}

  
  
  
  
