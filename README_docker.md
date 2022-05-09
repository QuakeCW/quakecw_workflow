# Running quakecw_workflow as a Docker Image
CWNU Earthquake Research Group's Adaptation of QuakeCoRE NZ workflow

Korean Ground Motion Simulation @ Nurion

배성은(University of Canterbury, QuakeCoRE 소프트웨어 팀장 / 창원대학교 BP Fellow)

# 도커 허브

도커 이미지를 최신 버전으로 업데이트 한다.

```
docker pull glorykingsman/quakekorea
```

[1] 종종 도커허브가 Permission Denied같은 에러를 일으키는 경우 (특히 `docker push`시) `docker login -u 사용자ID -p 비밀번호` 명령어를 사용해 도커허브에서 허용한 collaborator 계정으로 다시 로그인해줘야 함.
리눅스에서 `docker info`같은 기본적인 명령어가 퍼미션 에러를 일으키는 경우, docker 그룹에 현재 사용자가 포함되어 있나 확인할 것
```
(py39) seb56@hypocentre:~$ docker ps -s
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/json?size=1": dial unix /var/run/docker.sock: connect: permission denied

(py39) seb56@hypocentre:~$ sudo usermod -aG docker seb56
(py39) seb56@hypocentre:~$ groups
seb56 sudo qcore ucqcore
(py39) seb56@hypocentre:~$ newgrp docker
(py39) seb56@hypocentre:~$ groups
docker sudo seb56 qcore ucqcore
(py39) seb56@hypocentre:~$ docker ps -s
CONTAINER ID  IMAGE           COMMAND  CREATED     STATUS     PORTS   NAMES       SIZE
e4b218ba9ac9  glorykingsman/quakekorea  “bash”  24 minutes ago  Up 24 minutes       competent_lamarr  7.85MB (virtual 47.9GB)
```
# QuakeData 다운로드 및 압축 풀기 (최초 한번만)

QuakeData 압축 파일을 다운 받아 압축을 풀어준다. `C:\Users\GloryKim`에 `QuakeData`라는 폴더가 생성되었다고 가정하자. 

다운로드 링크: https://1drv.ms/u/s!As4Rczo4lNsOh7V1zlzOEX7FkySpmA?e=H7asYg


BB 다운로드 링크: https://1drv.ms/u/s!As4Rczo4lNsOh7Vyap05_WrBbahiEA?e=dNpSUq

# 도커 컨테이너 시작

위에서 압축을 푼 `C:\Users\GloryKim\QuakeData`라는 디렉토리를 마운트하면서 도커 컨테이너를 실행시킨다.
```
docker run -it --user 1000:1000 -v C:\Users\GloryKim\QuakeData\:/home/quakekorea/QuakeData glorykingsman/quakekorea bash

```
도커 이미지 속에 quakekorea라는 유저 (UID 1000)와 그룹 (GID 1000)을 만들어두었으며, 이 이미지를 quakekorea 어카운트를 사용하여 실행하도록 강제하였다. QuakeData 디렉토리를 마운트함으로써 도커 컨테이너와 도커 바깥 환경(윈도우,리눅스)에서 동시에 억세스할 수 있게 된다. 시뮬레이션 인풋이나 시뮬레이션 결과값을 저장하는 위치로 사용하도록 한다.

![QuakeData](https://user-images.githubusercontent.com/466989/165229631-0ab1b399-4963-4cbe-b9de-7a3c3e3f9aa8.png)



위 실행 명령어는 배치파일 (or 스크립트)를 만들어 실행시키면 편하다.

```
./dockerun.bat
```

# quakecw_workflow 최신버전 받기
QuakeData 디렉토리 안에 quakecw_workflow를 최신 버전으로 업데이트 하도록 한다.
```
cd ~/QuakeData/quakecw_workflow
git pull 
```

# 시뮬레이션 실행
도커 컨테이너 안에서 시뮬레이션을 실행시키는 과정을 서술함. README.md에 있는 내용과 겹치는 내용은 제외하고, 도커 컨테이너의 예외적인 부분에 대해서 중점적으로 다룰 것임.
$QUAKECW (.bashrc에 설정되어 있음)으로 가서 디렉토리를 만들자.
```
(python3_local) quakekorea@a5fe9fb8917e:~/QuakeData/quakecw_workflow$ cd $QUAKECW
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow$ mkdir -p RunFolder/Pohang
```


## 단층 모델 (Source)
위에서 만든 Pohang 디렉토리 아래에 Source 디렉토리를 만들고 (엄밀히 말하면 위치는 자유이나 정리된 디렉토리 구조를 이용하면 여러가지 수고를 덜 수 있다.)
미리 설정되어 있는 `source_docker.yaml`을 가져와서 참고/수정해 사용하도록 하자.

```
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow$ cd RunFolder/Pohang
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ mkdir Source
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ cd Source
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang/Source$ cp $QUAKECW/Source/source_docker.yaml .
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
VELOCITY_MODEL: "/home/quakekorea/quakecw_workflow/Source/kr_gb_kim2011_modified.1d"
SOURCE_DATA_DIR: "/home/quakekorea/quakecw_workflow/RunFolder/Pohang/Source"
```

여기에서, `SOURCE_DATA_DIR`은 생성된 단층모델 데이터를 저장할 위치를 의미한다. 우리는 방금전 만든 디렉토리에 단층모델 데이터가 저장되도록 설정하였다. 

단층 모델 생성하는 명령어를 실행해 보자.
```
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang/Source$ python $QUAKECW/Source/make_source.py ./source_docker.yaml
Executing createSRF.py
2022-05-08 14:35:03,037 - Creating SRF with command: /opt/gmsim/Environments/qkorea/ROOT/local/gnu/bin/genslip_v3.3 read_erf=0 write_srf=1 read_gsf=1 write_gsf=0 infile=Srf/Pohang.gsf mag=5.400000 nx=41 ny=41 ns=1 nh=1 seed=103245 velfile=/home/quakekorea/quakecw_workflow/Source/kr_gb_kim2011_modified.1d shypo=0.000000 dhypo=2.036901 dt=0.010000 plane_header=1 srf_version=1.0 rvfrac=0.8 alpha_rough=0.01 slip_sigma=0.85
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
/opt/gmsim/Environments/qkorea/virt_envs/python3_local/lib/python3.8/site-packages/shapely/ops.py:42: ShapelyDeprecationWarning: Iteration over multi-part geometries is deprecated and will be removed in Shapely 2.0. Use the `geoms` property to access the constituent parts of a multi-part geometry.
  source = iter(source)
WARNING:root:maximum allowed iterations reached while optimizing the alpha parameter
surface [WARNING]: Your grid dimensions are mutually prime.  Convergence is very unlikely.
surface [WARNING]: 557 unusable points were supplied; these will be ignored.
surface [WARNING]: You should have pre-processed the data with block-mean, -median, or -mode.
surface [WARNING]: Check that previous processing steps write results with enough decimals.
surface [WARNING]: Possibly some data were half-way between nodes and subject to IEEE 754 rounding.
```

위와 비슷한 형태의 출력값이 나왔다면 잘 진행되고 있다고 이해해도 좋다.

`.bashrc`에 설정된 `tree`라는 명령어를 실행해 이 디렉토리의 구조를 살펴보도록 하자.
```
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang/Source$ tree
.
 |-__pycache__
 | |-setSrfParams.cpython-38.pyc
 | |-srf_config.cpython-38.pyc
 |-Stoch
 | |-Pohang.stoch <--------------- 
 |-Srf
 | |-Pohang.info
 | |-Pohang.SEED
 | |-Pohang_map.png
 | |-Pohang_slip_rise_rake.png
 | |-Pohang.gsf
 | |-Pohang.srf.  <---------------
 |-srf_config.py
 |-source_docker.yaml
 |-setSrfParams.py
 |-createSRF_log.txt
 |-createSRF.py
 |-cnrs.txt
```

Pohang.stoch과 Pohang.srf가 보인다면 성공적으로 단층모델이 생성되었음을 의미한다.

Pohang_slip_rise_rake.png와 
Pohang.stoch과 Pohang.srf가 보인다면 성공적으로 단층모델이 생성되었음을 의미한다.
Pohang_map.png과 Pohang_slip_rise_rake.png은 만들어진 단층 모델의 위치와 형상을 시각화한 것이다.

![Pohang_map](https://user-images.githubusercontent.com/466989/167283932-b27f1feb-dcda-4ecc-9bd8-8d8ddec4d135.png)

![Pohang_slip_rise_rake](https://user-images.githubusercontent.com/466989/167283937-78833265-32e7-4412-b8bd-3ef212a4a5ff.png)

## 속도 모델
속도모델은 하드웨어 리소스 부족으로 현재까지 도커 컨테이너 상에서 만드는 것이 불가능해 보인다. 첨부한 샘플 속도 모델을 사용하도록 한다.

```
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ ln -s $QUAKECW/VM/sample_vm_h1.0/ VM
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ cd VM
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang/VM$ ls
VeloModCorners.txt  gridout_rt01-h1.0       model_coords_rt01-h1.0  nzvm.cfg     vm_params.yaml               vp3dfile.p
gridfile_rt01-h1.0  model_bounds_rt01-h1.0  model_params_rt01-h1.0  rho3dfile.d  vm_params2vm_Pohang_log.txt  vs3dfile.s

```
vp3dfile.p, vs3dfile.s 그리고 rho3dfile.d가 속도모델을 구성하는 3개의 파일들이다. 나머지 model.., grid..파일들은 속도모델의 위치와 도메인에 관련해 생성된 부산물이며, 시뮬레이션에서 참조되기도 하므로 지우거나 수정하지 않도록 한다.


## 관측소 리스트
관측소 리스트는 속도모델을 만드는데 사용한 `vm_params.yaml`을 사용하는데, 속도 모델 도메인 내에 2km단위의 그리드를 만들어 가상의 관측점을 생성해낸다. 추가로 실제 관측소 좌표리스트를 더할 수 있는 옵션 `--real_stats`을 이용하면 차후 관측 데이터와 비교 분석하는데 용이하다.
```
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ python $QUAKECW/Stations/make_stations.py VM/vm_params.yaml --real_stats $QUAKECW/Stations/realstations_20220420.ll --outdir Stations --name Busan_2km
created temp dir VM/tmpgewn73x7
python /home/quakekorea/QuakeData/quakecw_workflow/Stations/extract_Vs30.py Stations/Busan_2km.ll
input .ll file: Stations/Busan_2km.ll
output .v30 file: Stations/Busan_2km.vs30

(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ cd Stations/
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang/Stations$ ls
Busan_2km.ll  Busan_2km.vs30

```
만약  Busan_2km.vs30가 보이지 않는다면, $QUAKECW/Stations에 global_vs30.tif파일이 있는지 확인해볼 것. 최신 버전은 다음 링크를 방문해, Vs30 Raster Download를 클릭하면 다운 받을 수 있다. https://usgs.maps.arcgis.com/apps/webappviewer/index.html?id=8ac19bc334f747e486550f32837578e1


## 시뮬레이션 인스톨

첨부된 `gmsim_docker.yaml`을 사용해서 시뮬레이션을 인스톨 하도록 하자. 이 예시에서는 아무 수정없이 사용 가능하나, 다른 경우에는 sim_root_dir, source_data, vm_data, stat_file등의 위치에 따라 적절히 수정해서 사용하도록 한다.

```
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ cp $QUAKECW/gmsim_docker.yaml .
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ cat ./gmsim_docker.yaml
workflow: /opt/gmsim/Environments/qkorea/workflow
sim_root_dir: /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang
fault_name: Pohang
source_data:  /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Source
copy_source_data: False
vm_data: /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/VM
copy_vm_data: False
gmsim_template: /home/quakekorea/QuakeData/gmsim_templates/Pohang_sdrop50_h1.0
stat_file: /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Stations/Busan_2km.ll
n_max_retries: 2
```

이 예에서 hh=1.0을 사용하는 관계로 시뮬레이션에서 LF와 HF의 경계가 되는 주파수 flo가 0.1이 되어야 함 (flo = 0.1/hh). 
참고로, `gmsim_docker.yaml`에 예시로 설정되어 있는 gm_templates은 `Pohang_sdrop50_h1.0` 으로 그 내용은 아래와 같다.

```
(python3_local) quakekorea@23b6d4e0f021:~/quakecw_workflow$ cat /home/quakekorea/QuakeData/gmsim_templates/Pohang_sdrop50_h1.0/root_defaults.yaml
hf:
  version: 5.4.5.3
  dt: 0.005
  rvfac: 0.5
  sdrop: 50
  path_dur: 2
  kappa: 0.016
bb:
  fmin: 0.2
  fmidbot: 0.5
  no-lf-amp: True
emod3d:
   emod3d_version: 3.0.4
ims:
  extended_period: False
  component:
    - geom
  pSA_periods: [0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.1, 0.12, 0.15, 0.17, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.5, 10.0]
flo: 0.1
dt: 0.005
v_1d_mod: kr_gb_kim2011_modified.1d
```

모두 준비되었다면 아래 명령어를 실행시켜 시뮬레이션을 인스톨하도록 하자. 도커 컨테이너에서 인스톨할 때는 반드시 *--console* 옵션을 써야 한다는 점을 유의하도록 한다. 이 옵션을 없에면 디폴트 작동 방식인 `qsub`를 이용한 인스톨 관련 명령어 서브밋을 시도하는데, 도커 이미지안에는 PBS가 없기 때문에 에러가 발생한다.

```
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ python $QUAKECW/install_gmsim.py gmsim_docker.yaml
Pohang 1r

python /opt/gmsim/Environments/qkorea/workflow/workflow/automation/install_scripts/install_cybershake.py /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/fault_list.txt /home/quakekorea/QuakeData/gmsim_templates/Pohang_sdrop50_h1.0 --stat_file_path /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Stations/Busan_2km.ll --keep_dup_station
Version path: /home/quakekorea/QuakeData/gmsim_templates/Pohang_sdrop50_h1.0
2022-05-08 15:55:58,034 - Installing /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Data/Sources/Pohang/Srf/Pohang.srf
****************************************************************************************************
2022-05-08 15:55:58,039 - installing bb
****************************************************************************************************
2022-05-08 15:55:58,039 -                                      EMOD3D HF/BB Preparation Ver.slurm
****************************************************************************************************
2022-05-08 15:55:58,039 - installing bb finished
2022-05-08 15:55:58,053 - /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Stations/Busan_2km.ll
2022-05-08 15:55:58,053 - From: /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Stations/Busan_2km.ll. To: /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Runs/Pohang/fd_rt01-h1.0.statcords, /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Runs/Pohang/fd_rt01-h1.0.ll


================================
             Source
================================
/home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Data/Sources/Pohang/setSrfParams.py
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
/home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Data/VMs/Pohang/vm_params.yaml
{'GRIDFILE': './gridfile_rt01-h1.0',
 'GRIDOUT': './gridout_rt01-h1.0',
 'MODEL_BOUNDS': './model_bounds_rt01-h1.0',
 'MODEL_COORDS': './model_coords_rt01-h1.0',
 'MODEL_LAT': 35.5755,
 'MODEL_LON': 128.9569,
 'MODEL_PARAMS': './model_params_rt01-h1.0',
 'MODEL_ROT': 0.0,
 'centroidDepth': 4.05399,
 'code': 'rt',
 'extent_x': 250,
 'extent_y': 400,
 'extent_zmax': 40,
 'extent_zmin': 0.0,
 'extracted_slice_parameters_directory': 'SliceParametersNZ/SliceParametersExtracted.txt',
 'flo': 0.1,
 'hh': 1.0,
 'mag': 5.5,
 'min_vs': 0.2,
 'model_version': 'KVM_21p6',
 'nx': 250,
 'ny': 400,
 'nz': 40,
 'output_directory': 'output',
 'sim_duration': 60,
 'sufx': '_rt01-h1.0',
 'topo_type': 'BULLDOZED'}
================================
       GMSIM template
================================
/home/quakekorea/QuakeData/gmsim_templates/Pohang_sdrop50_h1.0/root_defaults.yaml
{'bb': {'fmidbot': 0.5, 'fmin': 0.2, 'no-lf-amp': True},
 'dt': 0.005,
 'emod3d': {'emod3d_version': '3.0.4'},
 'flo': 0.1,
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
Simulation installed at /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang
Run with : $QUAKECW/run_gmsim.sh /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/gmsim_docker.yaml
```


## 시뮬레이션 실행

인스톨이 완료되면서 알려주는 명령어를 실행시키면 시뮬레이션이 시작된다.

```
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow$ cd RunFolder/Pohang
(python3_local) quakekorea@a5fe9fb8917e:~/quakecw_workflow/RunFolder/Pohang$ $QUAKECW/run_gmsim.sh /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/gmsim_docker.yaml
sim_root_dir: /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang
workflow: /opt/gmsim/Environments/qkorea/workflow
n_max_retries: 2
python /opt/gmsim/Environments/qkorea/workflow/workflow/automation/execution_scripts/run_cybershake.py /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/task_config.yaml --n_max_retries 2
2022-05-08 18:21:26,167 - MainThread - Logger file added
2022-05-08 18:21:26,169 - MainThread - Master script will run [<ProcessType.EMOD3D: 1>, <ProcessType.HF: 4>, <ProcessType.BB: 5>, <ProcessType.IM_calculation: 6>, <ProcessType.clean_up: 11>]
2022-05-08 18:21:26,169 - MainThread - Created queue_monitor thread
2022-05-08 18:21:26,169 - MainThread - Created main auto_submit thread
2022-05-08 18:21:26,169 - MainThread - Started main auto_submit thread
2022-05-08 18:21:26,175 - queue monitor - Running queue-monitor, exit with Ctrl-C.
2022-05-08 18:21:26,177 - main auto submit - Loaded root params file: /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Runs/root_params.yaml
2022-05-08 18:21:26,177 - MainThread - Started queue_monitor thread
2022-05-08 18:21:26,182 - main auto submit - Number of runnable tasks: 2
2022-05-08 18:21:26,182 - main auto submit - Tasks to run this iteration: Pohang-EMOD3D
2022-05-08 18:21:31,188 - queue monitor - Updating 1 mgmt db tasks.
2022-05-08 18:21:31,188 - queue monitor - Acquiring db connection.
2022-05-08 18:21:31,188 - queue monitor - Received entry SchedulerTask(run_name='Pohang', proc_type=1, status=3, job_id=None, error=None), status is more than created but the job_id is not set.
2022-05-08 18:21:36,208 - queue monitor - Task 'EMOD3D' on 'Pohang' not found on ps or in the management db folder; resetting the status to 'created' for resubmission
start_time not in proc_Data.keys(),value 0

end_time not in proc_Data.keys(),value 0

run_time not in proc_Data.keys(),value 0

cores not in proc_Data.keys(),value 1

status not in proc_Data.keys(),value RUNNING

2022-05-08 18:21:36,210 - queue monitor - Updating 1 mgmt db tasks.
2022-05-08 18:21:36,210 - queue monitor - Received entry SchedulerTask(run_name='Pohang', proc_type=1, status=7, job_id=None, error='Disappeared from ps. Creating a new task.'), status is more than created but the job_id is not set.
2022-05-08 18:27:47,120 - queue monitor - Received entry SchedulerTask(run_name='Pohang', proc_type=4, status=7, job_id=None, error='/home/quakekorea/QuakeData/RunFolder/Pohang/Runs/Pohang/Pohang/HF/Acc/HF.bin /home/quakekorea/QuakeData/quakecw_workflow/RunFolder/Pohang/Runs/Pohang/fd_rt01-h1.0.ll The waveform for station 005D49 contains all zeros, please investigate.'), status is more than created but the job_id is not set.
...


```

시뮬레이션이 모두 수행되면 최종적으로 Runs/Pohang/Pohang/{LF,HF,BB,IM_calc,verification} 디렉토리에 결과물들이 위치하게 된다.


# 도커 컨테이너 업데이트

도커 컨테이너 안에서 수정이 이루어진 경우. 공유 디럭테로인 QuakeData에 수정, 저장한 파일을 제외한 모든 변화는 도커 컨테이너가 종료되는 시점에 사라진다. 시스템 내의 프로그램이나 코드를 업데이트하였고, 그 것이 보존되기를 원한다면 아래 안내를 따르도록 한다.

도커 컨테이너 상에서 Ctrl P Ctrl Q를 눌러 바깥으로 빠져나감.

```
(py39) seb56@hypocentre:~$ docker ps -s
CONTAINER ID   IMAGE          COMMAND   CREATED       STATUS       PORTS     NAMES              SIZE
e4b218ba9ac9   97f8cfdb63d6   "bash"    4 hours ago   Up 4 hours             competent_lamarr   8.16MB (virtual 47.9GB)
```
컨테이너 ID를 확인하고 커밋을 실행.

```
(py39) seb56@hypocentre:~$ docker commit e4b218ba9ac9 glorykingsman/quakekorea
sha256:cb61456c364019f00dc20b0d6247b690e26a426d19dd5c0c65ad6a9ebfaa49ab
```
커밋이 끝나고, 도커 허브에 업로드.

```
(py39) seb56@hypocentre:~$ docker push glorykingsman/quakekorea
Using default tag: latest
The push refers to repository [docker.io/glorykingsman/quakekorea]
fa27d19b34ec: Pushed
6891eff9632e: Layer already exists
38dd9180de23: Layer already exists
21715aed4f7d: Layer already exists
35981d72a469: Layer already exists
afbaee486fbc: Layer already exists
004b095b6594: Layer already exists
dc270c15779d: Layer already exists
4ed94b3e2f43: Layer already exists
d8b799da3b90: Layer already exists
64fc6418a083: Layer already exists
f45638541d8e: Layer already exists
e71d5994aaeb: Layer already exists
867d0767a47c: Layer already exists
latest: digest: sha256:8e3f069bf56df43233984cd3acaaeb70b9417db1f4e398043b2209ebf21debb2 size: 3281
```

다시 도커 컨테이너 안으로 들어가려면

```
docker attach e4b218ba9ac9
```
