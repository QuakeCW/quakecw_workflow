# quakecw_workflow
CWNU Earthquake Research Group's Adaptation of QuakeCoRE NZ workflow

Korean Ground Motion Simulation @ Nurion

배성은(University of Canterbury, QuakeCoRE 소프트웨어 팀장 / 창원대학교 BP Fellow)

# 시뮬레이션


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
```


마지막 라인은 Pohang의 EMOD3D와 HF job들이 현재 Queue에 추가되어 실행을 기다리고 있음을 알려줌

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


Cybershake 실행할 때 제공한 task_config.yaml에서 요청한 바에 따라 워크플로우는 인스톨된 단층모델들, Pohang 각 1개씩의 realisation의 저주파(LF, 주로 EMOD3D로 불리움), 고주파(HF), BB (broadband = LF+HF) 등의 job을 누리온에 자동으로 submit하고 각 job의 진행상황을 모니터함과 동시에,의존도가 충족되면 다음 단계의 job을 다시 submit하고 모니터링한다.

job을 서브밋할 때, 필요한 리소스와 wallclock 같은 변수도 자동으로 예상하여 그 값을 사용하는데, 만약 작업시간이 예상을 초과하여 계산이 중단되면, 예상시간을 늘여서 다시 서브밋하도록 제작되어 있음. (2차 시도는 시간 2배, 3차 시도는 시간 3배..)

위와 같은 이유로 시뮬레이션이 아직 안정화되지 못한 경우, 다양한 이유로 job이 실패할 수 있으나 그럴 때마다 예상시간을 늘이며 다시 서브밋된다면 누리온 계정의 allocation을 낭비하게 될 수도 있음. 따라서 이 워크플로우는 시뮬레이션이 이미 안정화 단계에 있을 때 사용하는 것을 권장함.

한편, run_cybershake.py는 디폴트값으로 최고 2번의 시도를 하도록 되어 있으며, 2차 시도 끝에도 계산이 제대로 끝나지 못했다면 다음 방법을 이용해 재시도해볼 수 있다.


### 재시도

만약 정해진 횟수 내에 어떤 이유로 계산이 성공적으로 완료되지 않았다면, 그 원인을 수정한 다음,--n_max_retries 스위치와 함께다시 run_cybershake.py를 실행하면 된다.  
  
예시) BB를 2회 시도하였으나, .vs30 파일이 지정된 위치에 있지 않은 이유로 run_cybershake.py가 BB를 계산하지 못한 상황에서 종료가 되었다고 가정. 원인을 해결하고, 아래와 같이 --n_max_retries 3 을 주어 재실행시키면 이전의 2회 시도에 이어 한번 더 시도하게 된다.  
  

```
(python3_nurion) x2319a02@login02:/scratch/x2319a02/gmsim/RunFolder/Pohang_20220417> python /home01/x2319a02/gmsim/Environments/v211213/workflow/workflow/automation/execution_scripts/run_cybershake.py `pwd` $USER `pwd`/task_config.yaml --n_max_retries 3
```


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



각각의 job의 현재 상태를 파악하고 싶다면 screen을 잠시 빠져나오거나 (detach, Ctrl+a d), 다른 터미널에서 아래와 같은 방법을 사용할 수 있다.


#### LF (EMOD3D)

LF/Rlog디렉토리에 \*.rlog파일이 업데이트 되는 과정을 관찰하면 됨

| (python3_nurion) x2319a02@login04:/scratch/x2319a02/gmsim/RunFolder/Busan20211214/Runs/Pohang/Pohang/LF/Rlog> tail -f Pohang-00539.rlog\*\*\*\* Dumping wavefield to restart file:/scratch/x2319a02/gmsim/RunFolder/Busan20211214/Runs/Pohang/Pohang/LF/Restart/Pohang_rst-00539.e3d\*\*\*\* Dumping all output files to:/scratch/x2319a02/gmsim/RunFolder/Busan20211214/Runs/Pohang/Pohang/LF/OutBin...DONE2000 30.27 4417.19 1.00 67.07 0.96 1086. 0.992100 16.17 4417.19 1.00 52.03 1.00 1138. 1.002200 16.38 4417.19 1.00 52.49 1.00 1191. 1.002300 15.75 4417.19 1.00 51.98 1.00 1243. 1.002400 15.66 4417.19 1.00 51.89 1.00 1295. 1.00    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |

현재까지 timestep 2400을 수행했음을 알려줌.

LF/e3d.par의 nt값을 확인하면 timestep이 12200에 도달할 때까지 계산이 지속되어야 함을 알수 있음.


#### HF

HF/Acc에 HF.bin, HF.log 파일 사이즈가 증가하는 것이 관찰되면 정상적으로 작동하고 있다고 짐작할 수 있음

  


| (python3_nurion) x2319a02@login04:/scratch/x2319a02/gmsim/RunFolder/Busan20211214/Runs/Pohang/Pohang/HF/Acc> ls -ltrtotal 1455080\-rw-rw-r-- 1 x2319a02 re0016 8 Oct 21 09:52 SEED\-rw-rw-r-- 1 x2319a02 re0016 5169992 Oct 21 09:54 HF.log\-rw-rw-r-- 1 x2319a02 re0016 1610809808 Oct 21 09:54 HF.bin |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

계산이 모두 끝나면 LF와 HF 모두 결과값이 원하는 포맷과 일치하는지 간단한 검증 과정을 거친다. 통과하면 Complete로 마크되고 그 다음 단계에 계산할 job이 있다면 (이 경우 BB) submit하게 된다.






# 인풋 모델 만들기

단층, 속도 모델을 만드는 것도 Cybershake 워크플로우에서 커버할 수 있으나, 이 워크플로우는 적은 수의 모델을 실험적으로 생성, 테스트하는 데에는 최적화되어 있지 않으므로, 약간의 수작업을 통해 인풋 모델 만드는 방법을 우선 소개함.


## 단층 모델 만들기

TO DO: Stoch모델이 만들어질 때, 저장되는 위치가 Stoch/{fault name}/{fault name}.stoch 이 되어버리는 버그가 있다. Stoch/{fault name}.stoch이 맞음 (setSrfParams.py에서 STOCH=Stoch 이면 정상 작동)

setSrfParams.py 을 수정한 다음 createSRF.py를 실행

| \## Sets Variables for SRF/Stoch Generation\# TYPE:\# 1: point source to point source srf\# 2: point source to finite fault srf\# 3: finite fault to finite fault srf\# 4: multi-segment finite fault srfTYPE = 2\# specify basename for gsf, srf and stoch file created\# PREFIX for gsf/srf/stoch files\# if prefix ends with '\_', automatic naming followsPREFIX = 'Srf/Gyeongju'\# directory for Stoch file(s)\# set to None to not produce the stoch fileSTOCH = 'Stoch/Gyeongju'\###\### COMMON PARAMETERS (apply to all types but multi)\###\# latitude (float)LAT = 35.79\# longitude (float)LON = 129.12\# depth (float)DEPTH = 20\# magnitude (float)MAG = 5.8\# strike (int)STK = 24\# dip (int)DIP = 70\# rake (int)RAK = 176\# rupture timestepDT = 0.01       |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |





## 속도 모델 만들기


### 준비

NZVM code에서 부산 분지 모델이 추가된 버전의 바이너리 위치는  
  


/home01/hpc11a04/gmsim/VM_KVM/Velocity-Model-Viz/Velocity-Model/NZVM (2021년 Oct 4 build) (To do: github 에서 maintain)

  


/scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Pohang/vm_params.yaml 을 적절히 수정해서 사용

| mag: 5.5centroidDepth: 4.05399MODEL_LAT: 35.5755MODEL_LON: 128.9569MODEL_ROT: 0.0hh: 0.1min_vs: 0.2model_version: KVM_21p6topo_type: BULLDOZEDoutput_directory: outputextracted_slice_parameters_directory: SliceParametersNZ/SliceParametersExtracted.txtcode: rtextent_x: 250extent_y: 400extent_zmax: 40extent_zmin: 0.0sim_duration: 60flo: 1.0nx: 2500ny: 4000nz: 400sufx: \_rt01-h0.100 |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

model_version: KVM_21p6은 부산 분지 모델이 들어간 버전임을 의미함

hh: 0.1은 그리드 간격이 100m를 의미함

extent_x = hh \* nx

extent_y = hh \* ny

extent_zmax-extent_zmin=hh\*nz

의 관계가 있음

flo = 0.1 / hh 의 상관 관계가 있음

hh=0.1 --> flo: 1.0

hh=0.4 --> flo: 0.25


### 실행  
  


“Pohang2”라는 모델을 만들기로 함.

만약 가상환경이 활성화가 되지 않은 상황이라면,

activate_env /home01/x2319a02/gmsim/Environments/v211213/

디렉토리로 이동하여 아래 순서들을 진행한 후, make_vm.pbs를 서브밋한다.

cd /scratch/x2319a02/gmsim/Busan_Data/Data/VMs

mkdir Pohang2

cd Pohang2

cp /scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Pohang/vm_params.yaml .

(편집, 수정)  
  


cp /scratch/x2319a02/gmsim/Busan_Data/utils/VM/\* .

make_vm.pbs 파일을 체크하고 올바른 버전의 NZVM 바이너리가 사용되는지 확인. Walltime 은 남한 대부분을 커버하는 100m 모델의 경우 10시간 정도 세팅이 적당함

​​  
  


qsub -v REL_NAME=Pohang2,VM_PARAMS_YAML=\`pwd\`/vm_params.yaml,OUTPUT_DIR=\`pwd\` -V /scratch/x2319a02/gmsim/Busan_Data/utils/VM/make_vm.pbs

qsub -v VM_PARAMS_YAML=\`pwd\`/vm_params.yaml,OUTPUT_DIR=\`pwd\`,REL_NAME=Busan -V /scratch/x2319a02/gmsim/Busan_Data/utils/VM/make_vm.pbs


### 진행상황 체크

(python3_nurion) x2319a02@login04:/scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Pohang2> qstat -u $USER

pbs:

Req'd Req'd Elap

Job ID Username Queue Jobname SessID NDS TSK Memory Time S Time

\-------------------- -------- -------- ---------- ------ --- --- ------ ----- - -----

9180242.pbs x2319a02 normal NZVM 15846 1 68 -- 04:00 R 00:04

Job ID를 참고하여, 현재 $HOME 디렉토리에서 임시로 쓰여지고 있는 아웃풋 파일의 업데이트 상황을 모니터할 수 있다

(python3_nurion) x2319a02@login04:/scratch/x2319a02/gmsim/Busan_Data/Data/VMs/Pohang2> tail -f $HOME/pbs.9180242.pbs.x8z/9180242.pbs.OU

Completed loading of global surfaces.

Loading basin data.

Loading KVM_21p6 perturbation files.

Completed Loading of perturbation files.

All basin surfaces loaded.

All basin boundaries loaded.

All basin sub model data loaded.

Completed loading basin data.

All global data loaded.

Generating velocity model3% complete.


### 생성파일 체크

위에서 서브밋한 pbs스크립트는 64코어를 이용해 NZVM을 실행시켜 \*.p, \*.s, \*.d 파일을 생성시키고, gen_coords.py를 불러 model_params, model_bounds, model_params 등과 같은 좌표 파일들을 도메인에 맞게 생성해낸다. 아래와 같은 파일들이 최종적으로 디렉토리에 상주하게 됨

  


|  \|-VMs\| \|-Pohang2\| \| \|-vm_params.yaml\| \| \|-nzvm.cfg\| \| \|-vp3dfile.p\| \| \|-vs3dfile.s\| \| \|-rho3dfile.d\| \| \|-in_basin_mask.b\| \| \|-model_bounds_rt01-h0.100\| \| \|-model_coords_rt01-h0.100\| \| \|-model_params_rt01-h0.100\| \| \|-gridfile_rt01-h0.100\| \| \|-gridout_rt01-h0.100\| \| \|-VeloModCorners.txt |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |


## 관측소 리스트 만들기

속도모델을 생성하는 과정에서 부산물로 만들어지는 model_coords파일은 그리드 위의 좌표점들의 리스트이므로 이 것을 기반으로 시뮬레이션 관측점 리스트를 작성하기로 결정하였다. 하지만 위에서 생성한 model_coords파일은 hh=0.1으로, 100미터마다, 총 관측점이 1천만개에 달하여 시뮬레이션의 해상도를 필요이상으로 요구하게 되었다. 적절한 타협점으로 hh=2.0에서 25,000개의 관측점 좌표를 생성하게 되었다.  
  
python $gmsim/Pre-processing/VM/gen_coords.py .  
  


이 프로그램은 지정한 디렉토리 (이 경우 “.”)에서 vm_params.yaml을 찾아 지정한 값들에 맞추어 좌표파일들을 생성한다.

hh=2.0 에 맞추어 수정한 vm_params.yaml파일은 아래와 같다.

| mag: 5.5centroidDepth: 4.05399MODEL_LAT: 35.5755MODEL_LON: 128.9569MODEL_ROT: 0.0**hh: 2.0**min_vs: 0.2model_version: KVM_21p6topo_type: BULLDOZEDoutput_directory: outputextracted_slice_parameters_directory: SliceParametersNZ/SliceParametersExtracted.txtcode: rtextent_x: 250extent_y: 400extent_zmax: 40extent_zmin: 0.0sim_duration: 60**flo: 0.05****nx: 125****ny: 200****nz: 20**sufx: \_rt01-h2.000 |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

실행 후, 생성된 model_coords_rt01-h2.000을 아래와 같이 스테이션 리스트 파일로 바꿀수 있다.

/scratch/x2319a02/gmsim/Busan_Data/utils/VM/get_ll.sh ./model_coords_rt01-h2.000 Busan_2km_stats_20211018

Busan_2km_stats_20211018.ll

| 127.55618 37.35489 000000127.57877 37.35515 000001127.60136 37.35541 000002127.62395 37.35567 000003127.64655 37.35592 000004127.66913 37.35617 000005127.69171 37.35641 000006127.71431 37.35665 000007127.73691 37.35688 000008127.75949 37.35711 000009127.78207 37.35734 00000A127.80467 37.35756 00000B…130.03720 33.78315 00619B130.05881 33.78296 00619C130.08040 33.78276 00619D130.10201 33.78257 00619E130.12361 33.78236 00619F130.14522 33.78216 0061A0130.16682 33.78195 0061A1130.18842 33.78173 0061A2130.21002 33.78152 0061A3130.23163 33.78130 0061A4130.25323 33.78107 0061A5130.27484 33.78085 0061A6130.29645 33.78062 0061A7    |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

  


여기에 실존하는 관측점이나 관심 시설의 좌표를 추가하여 관측점 리스트를 완성하면 된다.

제일 아래에 빈 줄이 있으면 인스톨시에 에러가 뜨니 주의할 것

Vs30

extract_Vs30.py

관측 데이터 IM calc

python $gmsim/IM_calculation/IM_calculation/scripts/calculate_ims.py Obs_Acc a -o Obs_IM -np 40 -i Gyeongju -r Gyeongju -t s -c geom -s -p 0.01 0.02 0.03 0.04 0.05 0.075 0.1 0.12 0.15 0.17 0.2 0.25 0.3 0.4 0.5 0.6 0.7 0.75 0.8 0.9 1.0 1.25 1.5 2.0 2.5 3.0 4.0 5.0 6.0 7.5 10.0


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

  
  
  
  
