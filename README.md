# quakecw_workflow
CWNU Earthquake Research Group's Adaptation of QuakeCoRE NZ workflow

Korean Ground Motion Simulation @ Nurion

배성은(University of Canterbury, QuakeCoRE 소프트웨어 팀장 / 창원대학교 BP Fellow)

# 시뮬레이션



# 인풋 모델 만들기



## 단층 모델 만들기
Source 디렉토리의 `source.yaml`을 수정하거나 복사본을 만들어서 사용하도록 한다. 추후 알아보기 편하도록 적절한 이름을 선택해 저장해두도록 하자.

```
cp /scratch/x2319a02/gmsim/RunFolder/quakecw_workflow/Source/source.yaml /scratch/x2319a02/gmsim/RunFolder/quakecw_workflow/Source/source_Pohang.yaml
```
이 파일을 열어보면 단층의 특성에 관련된 내용들이 있다.
```
TYPE: 2
FAULT: Pohang
# latitude (float)
LAT: 36.109
# # longitude (float)
LON: 129.366
# # depth (float)
DEPTH: 7
# # magnitude (float)
MAG: 5.4
# # strike (int)
STK: 230
# # dip (int)
DIP: 69
# # rake (int)
RAK: 152
# # rupture timestep
DT: 0.01
VELOCITY_MODEL: "/home01/x2319a02/gmsim/VelocityModel/Mod-1D/kr_gb_kim2011_modified.1d"
SOURCE_DATA_DIR: "/scratch/x2319a02/gmsim/Busan_Data/Data/Sources/Pohang_20220421"
```

아래 명령어를 실행하면 단층 모델이 생성되어 `SOURCE_DATA_DIR`에 위치하게 됨

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/quakecw_workflow/Source> python make_source.py source_Pohang.yaml.yaml
```

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/Busan_Data/Data/Sources/Pohang_20220421> tree
.
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


/scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Pohang/vm_params.yaml 을 적절히 수정해서 사용 [1]

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/quakecw_workflow/VM> cat vm_params.yaml
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
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/quakecw_workflow/VM> python make_vm.py vm_params_1000.yaml Busan1000 --outdir /scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000 --ncores 16 --wallclock 2

Created: /scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000
Generated: /scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000/make_vm.pbs
Copyed vm_params_1000.yaml to /scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000
Submitted: qsub -V /scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000/make_vm.pbs
10082371.pbs
```

ncores은 노드 전체의 경우 68, wallclock 은 남한 대부분을 커버하는 100m 모델의 경우 15시간 정도 세팅이 적당하여 디폴트값으로 정해져 있으나 작은 사이즈의 예시로 사용하기 위해 옵션의 사용법을 제시하였다. 



### 진행상황 체크

속도 모델 생성 명령어를 실행할 때 사용한 `outdir`로 가 관찰해보겠다.
```
cd /scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000
```

아래와 같이 vm_params_1000.yaml의 복사본, 그리고 제출한 PBS스크립트이 위치해있다. 속도 모델이 생성되면 또한 이 곳에 위치하게 될 것이다.
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000> ls -ltr
total 8
-rw-rw-r-- 1 x2319a02 rd0624 574 Apr 21 23:11 vm_params_1000.yaml
-rw-rw-r-- 1 x2319a02 rd0624 896 Apr 21 23:11 make_vm.pbs
```

현재 진행 상활을 체크해 보도록 한다.
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000> qstat -u $USER

pbs:
                                                                 Req'd  Req'd   Elap
Job ID               Username Queue    Jobname    SessID NDS TSK Memory Time  S Time
-------------------- -------- -------- ---------- ------ --- --- ------ ----- - -----
10082371.pbs         x2319a02 normal   make_vm       --    1  68    --  02:00 Q   --
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000>
```
현재 이 job은 제출되어 대기중인 상태로 (Queued) 정상적으로 진행되면 Q->R (running) -> E (ending) 순으로 진행되는 과정을 볼수 있다. 총 2시간을 요청하였으며, 전체 코어가 68개인 노드에서 계산 될 예정이다 (다만 요청은 위에서 ncores =16으로 하였음) 

Job ID를 참고하여, 현재 $HOME 디렉토리에서 임시로 쓰여지고 있는 아웃풋 파일의 업데이트 상황을 모니터할 수 있다
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan1000> tail -f $HOME/pbs.10082371.pbs.x8z/10082371.pbs.OU
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

위에서 서브밋한 pbs스크립트는 64코어를 이용해 NZVM을 실행시켜 \*.p, \*.s, \*.d 파일을 생성시키고, gen_coords.py를 불러 model_params, model_bounds, model_params 등과 같은 좌표 파일들을 도메인에 맞게 생성해낸다. 아래와 같은 파일들이 최종적으로 디렉토리에 상주하게 됨

  


|  \|-VMs\| \|-Pohang2\| \| \|-vm_params.yaml\| \| \|-nzvm.cfg\| \| \|-vp3dfile.p\| \| \|-vs3dfile.s\| \| \|-rho3dfile.d\| \| \|-in_basin_mask.b\| \| \|-model_bounds_rt01-h0.100\| \| \|-model_coords_rt01-h0.100\| \| \|-model_params_rt01-h0.100\| \| \|-gridfile_rt01-h0.100\| \| \|-gridout_rt01-h0.100\| \| \|-VeloModCorners.txt |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |


## 관측소 리스트 만들기

관측소 리스트는 속도모델의 범위 안에서 가로 세로 2km마다의 간격으로 가상 관측소를 만들고, 실제로 존재하는 관측소 위치를 추가하여 만든다. 

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/quakecw_workflow/Stations> python make_stations.py ../VM/vm_params.yaml --real_stats /scratch/x2319a02/gmsim/Busan_Data/Stations/realstations_20220324.ll --outdir /scratch/x2319a02/gmsim/Busan_Data/Stations --name Busan_2km 
created temp dir ./tmpyaeod58j
input .ll file: /scratch/x2319a02/gmsim/Busan_Data/Stations/Busan_2km.ll
output .v30 file: /scratch/x2319a02/gmsim/Busan_Data/Stations/Busan_2km.vs30
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

단층 모델과 속도 모델이 준비되어 있다고 가정하고 시뮬레이션 실행법에 대해 기술하겠음. 단층 모델이나 속도 모델이 준비 되지 않았다면, 이 문서의 아랫부분에서 설명할 내용을 따라서 이들을 우선 생성하도록 할것.

KISTI 누리온 5호기에서 x2319a02계정으로 실행할 것임.

이 github 저장소를 클론하면 gmsim.yaml을 볼수 있는데, 이 파일을 템플렛처럼 사용하도록 한다.

```
workflow: /home01/x2319a02/gmsim/Environments/v211213/workflow
sim_root_dir: /scratch/x2319a02/gmsim/RunFolder/Pohang_20220417
fault_name: Pohang
source_data: /scratch/x2319a02/gmsim/Busan_Data/Data/Sources/Pohang_v2022_3
copy_source_data: False
vm_data: /scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Busan_20220324
copy_vm_data: False
gmsim_template: /home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/calculation/gmsim_templates/Pohang_22.03.13.3
stat_file: /scratch/x2319a02/gmsim/Busan_Data/Stations/Busan_2km_stats_20220414.ll
n_max_retries: 2
```

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
export TMOUT= #(= 다음에 아무 것도 추가하지 않고 엔터.)
screen
```

가상 환경을 활성화 해준다. (screen 세션이 시작될 때 기존에 있었던 가상 환경이 리셋됨)
```
activate_env /home01/x2319a02/gmsim/Environments/v211213
```
`activate_env` 명령어는 /home01/x2319a02/gmsim/share/bashrc.uceq 에 정의되어 있음 
./bashrc에 `source /home01/x2319a02/gmsim/share/bashrc.uceq` 를 추가하는 것을 추천함.

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
(python3_nurion) ..> python ./install_gmsim.py ./gmsim.yaml
```

yaml파일이 스크립트의 유일한 인풋으로, 필요에 따라 여러개의 yaml파일을 생성해서 사용할 수 있다.

실행 장면


```
Pohang 1r

qsub -V /scratch/x2319a02/gmsim/RunFolder/Pohang_20220417/install.pbs
b'10065872.pbs\n'
```
실행되는 과정에서 Pohang 단층의 realisation이 1개 (srf 파일의 갯수를 통해)임을 찾아내었으며, 인스톨하기 위한 명령어를 조합하여 install.pbs라는 PBS스크립트를 만들어 제출하였음을, 그리고, 제출한 job의 ID가 10065872라는 것을 알수 있다.

추가로 이 시뮬레이션 셋업에 관한 여러 정보들을 화면에 보여준다.
```
================================
             Source
================================
/scratch/x2319a02/gmsim/RunFolder/Pohang_20220417/Data/Sources/Pohang/setSrfParams.py
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
/scratch/x2319a02/gmsim/RunFolder/Pohang_20220417/Data/VMs/Pohang/vm_params.yaml
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
  GMSIM template:/home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/calculation/gmsim_templates/Pohang_22.03.13.3
================================
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
 
```


설치 진행 상황은 아래 명령어로 확인할 수 있다.   
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/Pohang_20220417> qstat -u $USER

pbs:
                                                                 Req'd  Req'd   Elap
Job ID               Username Queue    Jobname    SessID NDS TSK Memory Time  S Time
-------------------- -------- -------- ---------- ------ --- --- ------ ----- - -----
10066916.pbs         x2319a02 normal   serial_job  58196   1  68    --  01:00 R 00:05
```

S 항목의 R는 현재 이 Job이 Queue에 추가되어 실행중인 (Running) 상태임을 의미하며, 정상적인 상황이라면 Q->R->E  (Queued -> Running -> Ending) 순으로 진행된다.


Job이 진행되는 과정의 아웃풋은 같은 디렉토리 내의 serial_job.oXXXXXXXX 혹은 serial_job.eXXXXXXXX을 살펴보면 된다.

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder> cat serial_job.o10065872
2022-04-18 15:36:18,719 - Installing /scratch/x2319a02/gmsim/RunFolder/Pohang_20220417/Data/Sources/Pohang/Srf/Pohang.srf
****************************************************************************************************
2022-04-18 15:36:18,779 - installing bb
****************************************************************************************************
2022-04-18 15:36:18,780 -                                      EMOD3D HF/BB Preparation Ver.slurm
****************************************************************************************************
2022-04-18 15:36:18,780 - installing bb finished
2022-04-18 15:36:18,866 - /scratch/x2319a02/gmsim/Busan_Data/Stations/Busan_2km_stats_20220414.ll
2022-04-18 15:36:18,867 - From: /scratch/x2319a02/gmsim/Busan_Data/Stations/Busan_2km_stats_20220414.ll. To: /scratch/x2319a02/gmsim/RunFolder/Pohang_20220417/Runs/Pohang/fd_rt01-h0.100.statcords, /scratch/x2319a02/gmsim/RunFolder/Pohang_20220417/Runs/Pohang/fd_rt01-h0.100.ll
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


시뮬레이션 실행 디렉토리에 인스톨이 끝나면 아래와 같은 디렉토리 구조를 가지게 됨

```
.
 |-slurm_mgmt.db
 |-task_config.yaml
 |-mgmt_db_queue
 |-Data
 | |-Sources
 | | |-Pohang
 | |-VMs
 | | |-Pohang
 |-fault_list.txt
 |-Runs
 | |-Pohang
 | | |-Pohang
 | | | |-LF
 | | | |-HF
 | | | |-IM_calc
 | | | |-sim_params.yaml
 | | | |-BB
 | | |-fd_rt01-h0.100.statcords
 | | |-fd_rt01-h0.100.ll
 | | |-fault_params.yaml
 | |-root_params.yaml
 
```


## 시뮬레이션 실행

Cybershake 워크플로우를 인스톨하면 자동화 스케쥴러를 사용할 수 있다. 이 스케쥴러는 로그인 노드에서 상주하며 실행 중인 job을 모니터하고, 의존 관계에 있는 job들이 성공적으로 완료되면 그 다음 단계의 job을 자동으로 submit하는 기능이 있다.

quakecw_workflow 디렉토리 안으로 들어가거나, path를 적절히 보태어서 아래 명령을 실행한다.

```
(python3_nurion) ..> ./run_gmsim.sh ./gmsim.yaml
```

스크립트가 실행되면서 아래와 같은 아웃풋이 출력된다.
```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/quakecw_workflow> ./run_gmsim.sh gmsim.yaml
sim_root_dir: /scratch/x2319a02/gmsim/RunFolder/Pohang_20220417
workflow: /home01/x2319a02/gmsim/Environments/v211213/workflow
n_max_retries: 2
python /home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/automation/execution_scripts/run_cybershake.py /scratch/x2319a02/gmsim/RunFolder/Pohang_20220417 x2319a02 /scratch/x2319a02/gmsim/RunFolder/Pohang_20220417/task_config.yaml --n_max_retries 2

2022-04-18 17:13:46,439 - MainThread - Logger file added
2022-04-18 17:13:46,449 - MainThread - Master script will run [<ProcessType.EMOD3D: 1>, <ProcessType.HF: 4>, <ProcessType.BB: 5>, <ProcessType.IM_calculation: 6>, <ProcessType.merge_ts: 2>, <ProcessType.plot_ts: 3>, <ProcessType.IM_plot: 7>]
2022-04-18 17:13:46,453 - MainThread - Created queue_monitor thread
2022-04-18 17:13:46,454 - MainThread - Created main auto_submit thread
2022-04-18 17:13:46,455 - MainThread - Started main auto_submit thread
2022-04-18 17:13:46,455 - queue monitor - Running queue-monitor, exit with Ctrl-C.
2022-04-18 17:13:46,456 - MainThread - Started queue_monitor thread
2022-04-18 17:13:46,471 - main auto submit - Loaded root params file: /scratch/x2319a02/gmsim/RunFolder/Pohang_20220417/Runs/root_params.yaml
2022-04-18 17:13:46,619 - main auto submit - Number of runnable tasks: 2
2022-04-18 17:13:46,620 - main auto submit - Tasks to run this iteration: Pohang-EMOD3D, Pohang-HF
2022-04-18 17:13:47,139 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-04-18 17:13:47,143 - queue monitor - No entries in the mgmt db queue.
submit_time not in proc_Data.keys(),value 2022-04-18_17:13:46

submit_time not in proc_Data.keys(),value 2022-04-18_17:13:49

2022-04-18 17:13:52,571 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-04-18 17:13:52,577 - queue monitor - Updating 2 mgmt db tasks.
2022-04-18 17:13:52,577 - queue monitor - Acquiring db connection.
2022-04-18 17:13:58,198 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-04-18 17:13:58,199 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10067167-queued, Pohang-HF-10067168-queued
2022-04-18 17:13:58,202 - queue monitor - No entries in the mgmt db queue.
2022-04-18 17:14:04,816 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-04-18 17:14:04,818 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10067167-queued, Pohang-HF-10067168-queued
....
2022-04-18 19:30:04,246 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-04-18 19:30:04,248 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10067167-queued, Pohang-HF-10067168-running
....
2022-04-18 22:38:01,781 - queue monitor - Over 200 tasks were found in the queue. Check the log for an exact listing of them
2022-04-18 22:38:01,783 - queue monitor - In progress tasks in mgmt db:Pohang-EMOD3D-10067167-running
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
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/quakecw_workflow> python check_status.py ./gmsim.yaml

/home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/automation/execution_scripts/query_mgmt_db.py
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
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/quakecw_workflow> python check_status.py ./gmsim.yaml
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
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/Pohang20220328/Runs/Pohang/Pohang/LF/Rlog/tail -f Pohang-00000.rlog

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
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/Pohang20220328_2/Runs/Pohang/Pohang/HF/Acc> ls -ltr
total 6226180
-rw-rw-r-- 1 x2319a02 rd0624          8 Mar 28 09:17 SEED
-rw-rw-r-- 1 x2319a02 rd0624 6358882976 Mar 28 09:27 HF.bin
-rw-rw-r-- 1 x2319a02 rd0624   16652983 Mar 29 12:54 HF.log
```

계산이 모두 끝나면 LF와 HF 모두 결과값이 원하는 포맷과 일치하는지 간단한 검증 과정을 거친다. 통과하면 Complete로 마크되고 그 다음 단계에 계산할 job이 있다면 (이 경우 BB) submit하게 된다.




# 시각화

누리온 로긴 노드에서 직접 다양한 지도들을 생성할 수 있다.

IM_Calculation단계를 거쳐야 함.시뮬레이션 디렉토리에서 IM_calc디렉토리에 \*.csv파일이 존재하는 지 확인할 것.

  


IM Calculation 결과와 관측점의 위도/경도를 매칭해서 xyz파일을 생성해낸다.

IM_calc의 parent 디렉토리 (LF,HF,BB등이 있는 곳)로 가서 아래를 실행시킴

FAULT=Pohang

REL=Pohang

python $gmsim/visualization/im/spatialise_im.py IM_calc/${REL}.csv ../fd_rt01-h0.100.ll -o plot

위에서 non_uniform_im.xyz파일이 plot이라는 디렉토리에 생성되었을 것임. 아울러 im_order.txt라는 파일도 생겨나는데, 계산된 IM들의 순서가 기록된 파일임.

  
plot 디렉토리에 가서 아래 명령어를 입력. FAULT와 REL을 위처럼 변수로 지정해주면 다른 시뮬레이션 결과값에 대응할 수 있다.  
  


cd plot

python $gmsim/visualization/sources/plot_items.py -c**../../../../Data/Sources/${FAULT}/Srf/${REL}.srf** --xyz non_uniform_im.xyz -t **${FAULT}** --xyz-cpt-label \`cat im_order.txt\` -f **${FAULT}** --xyz-landmask --xyz-cpt hot --xyz-transparency 30 --xyz-grid --xyz-grid-contours --xyz-grid-search 12m --xyz-size 1k --xyz-cpt-invert --xyz-model-params **../../../../Data/VMs/${FAULT}/model_params_rt01-h0.100** -n 4

  
  


Plot_ts

자동으로 실행되도록 되어 있으나 (task_config.yaml) 현재 아래 문제로 종종 자동 실행이 안되는 경우가 있음.

  


| Traceback (most recent call last):File "/home01/x2319a02/gmsim/Environments/v211213//workflow/workflow/automation/execution_scripts/add_to_mgmt_queue.py", line 6, in &lt;module>from workflow.automation.lib.shared_automated_workflow import add_to_queueModuleNotFoundError: No module named 'workflow.automation'    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |

수동으로 실행해야 할 경우, 인스톨 시킨 디렉토리로 돌아가서 (Runs와 Data디렉토리를 포함한 곳) 아래를 실행

qsub -v XYTS_PATH=Runs/${FAULT}/${REL}/LF/OutBin/${REL}\_xyts.e3d,SRF_PATH=Data/Sources/${FAULT}/Srf/${REL}.srf,OUTPUT_TS_PATH=Runs/${FAULT}/${REL}/verification/${REL},MGMT_DB_LOC=\`pwd\`,SRF_NAME="${REL}" -V $gmsim/workflow/workflow/automation/org/kisti/plot_ts.pbs


# 관측 데이터

## 관측 데이터 변환
관측데이터들은 `/scratch/x2319a02/gmsim/Busan_Data/Data/Obs`에 보관되어 있다. 출처에 따라 KIGAM, KINS, KMA로 나뉘어져 있으며, 그 밑에 Pohang, Gyeongju등의 이벤트로 나뉘어져 있다.
해당 위치에서 qcore가 요구하는 형태 관측소.{000,090,ver} 포맷으로 전환하고, (예)` 171115_Acc_qcore`, 이들을 통합 저장소인 `/scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined`의 해당 이벤트에 위치한 `Obs_Acc`로 복사한다. (예) `/scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined/Pohang/Obs_Acc` 끝으로 convert_acc2vel.py 스크립트를 이용해 속도 데이터로 변환한다.

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/Busan_Data/Data/Obs/combined/Pohang> python ../../convert_acc2vel.py

```

## 관측 데이터 IM calc

python $gmsim/IM_calculation/IM_calculation/scripts/calculate_ims.py Obs_Acc a -o Obs_IM -np 40 -i Gyeongju -r Gyeongju -t s -c geom -s -p 0.01 0.02 0.03 0.04 0.05 0.075 0.1 0.12 0.15 0.17 0.2 0.25 0.3 0.4 0.5 0.6 0.7 0.75 0.8 0.9 1.0 1.25 1.5 2.0 2.5 3.0 4.0 5.0 6.0 7.5 10.0

## 관측 데이터와 시뮬레이션 결과값의 비교


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

  
  
  
  
