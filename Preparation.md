# 창원대 지진공학 및 방재 연구실 학생들을 위한 누리온/리눅스 워크스테이션 셋업 안내

## ssh
리눅스에서 누리온에서 손쉽게 접근하기 위해서 아래 셋업을 권장함. 한번만 시행하면 됨.

`nano ~/.ssh/config`

아래 내용을 집어넣고 User 항목에 자신의 로그인 어카운트 (예: x3336a02) 를 넣어준다.
```
Host *
  ControlMaster auto
  ControlPersist 1
  ServerAliveInterval 300
  ServerAliveCountMax 2
  ForwardX11 yes
  ForwardX11Trusted yes
  ControlPath ~/.ssh/sockets/ssh_mux_%h_%p_%r
  
Host nurion1
	User 로그인_어카운트
    Hostname 150.183.150.11
Host nurion2
	User 로그인_어카운트
    Hostname 150.183.150.12
Host nurion3
	User 로그인_어카운트
    Hostname 150.183.150.13
Host nurion4
	User 로그인_어카운트
    Hostname 150.183.150.14
Host nurion
	User 로그인_어카운트
	Hostname nurion.ksc.re.kr
Host nurion-dm
	User 로그인_어카운트
	Hostname nurion-dm.ksc.re.kr
```

그리고, `~/.ssh` 아래에 `sockets` 라는 디렉토리를 생성

`mkdir ~/.ssh/sockets`

새로 만든 디렉토리의 권한을 (755)로 설정
`chmod 755 ~/.ssh/sockets`

이제부터, `ssh nurion`, 혹은 `ssh nurion1...4`를 사용해서 누리온에 접속할 수 있으며, 터미널 한 곳이라도 연결이 되어 있다면, 다른 터미널에서 OTP와 비밀번호를 넣지 않고도 바로 접속이 가능해짐. 

```
ssh nurion
(x3336a02@150.183.150.12) Password(OTP):
(x3336a02@150.183.150.12) Password:
Last failed login: Mon May  2 15:29:22 KST 2022 from 1.219.251.31 on ssh:notty
There were 10 failed login attempts since the last successful login.
Last login: Sun May  1 20:35:13 2022 from 161.202.72.155
================ KISTI 5th NURION System ====================
 * Any unauthorized attempts to use/access the system can be
   investigated and prosecuted by the related Act
   (THE PROTECTION OF INFORMATION AND COMMUNICATIONS INFRASTRUCTURE)
....

x3336a02@login02:~>
```

`ssh nurion`이라고 하면 로그인 노드 1번부터 4번 중 하나가 자동 배정되며, `ssh nurion1...4`는 로그인 노드의 하나를 특정해서 접속할 수 있다. 시뮬레이션을 돌릴 때, 특정 노드를 지정하는 것이 편리할 때가 있음.

## 누리온 사용환경 설정
누리온에 최초로 접속하게 되면 ~/.ssh/config에 다음 내용을 추가해 GitHub를 SSH를 통해 사용할 수 있게 해주도록 한다.

```
Host github.com
    HostName ssh.github.com
    Port 443
    User git
```

~/.ssh에 위치한 id_rsa.pub 혹은 id_ecdsa.pub 파일을 GitHub Setting에 [등록](https://github.com/settings/keys) 해두면 GitHub와 Sync할 때마다 비밀번호를 넣어야 하는 번거로움을 덜 수 있다.


### 프로그램 패키지 인스톨

```
cd $HOME
mkdir -p project/cw
cd project/cw
git clone git@github.com:QuakeCW/quakecw_workflow.git 
cd project/cw/quakecw_workflow
./install.sh
```
위 명령어를 실행시키면 시뮬레이션을 위한 모든 소프트웨어와 데이터가 사용자의 홈디렉토리에 자동으로 다운로드 및 설치가 된다.
(실행 예시)
```
x3336a02@login04: ~/project/cw/quakecw_workflow$ ./install.sh
=== QuakeCW Installation ===
Home: /home01/x3336a02
Project: /home01/x3336a02/project
QuakeCW: /home01/x3336a02/project/cw/quakecw_workflow

Step 1: Downloading and extracting data archives...
  Velocity-Model_20260507.tar.gz already exists, skipping download
  Extracting Velocity-Model_20260507.tar.gz to /home01/x3336a02/project/cw...
  project_local_20260507.tar.gz already exists, skipping download
  Extracting project_local_20260507.tar.gz to /home01/x3336a02/project...
  quakecw_data_20260507.tar.gz already exists, skipping download
  Extracting quakecw_data_20260507.tar.gz to /home01/x3336a02/project/cw...

Step 2: Installing uv and Python 3.12.13...
Python 3.12.13 is already installed

Step 3: Creating Python virtual environment...
Using CPython 3.12.13
Creating virtual environment at: /home01/x3336a02/.local/quakecw_venv
✔ A virtual environment already exists at `/home01/x3336a02/.local/quakecw_venv`. Do you want to replace it? · yes
Activate with: source /home01/x3336a02/.local/quakecw_venv/bin/activate

Step 4: Installing PyPI packages from requirements.txt...
Using Python 3.12.13 environment at: /home01/x3336a02/.local/quakecw_venv
Resolved 58 packages in 390ms
Installed 58 packages in 4.36s
 + affine==2.4.0
 + alphashape==1.3.1
...
+ trimesh==4.11.5
 + typing-extensions==4.15.0
 + urllib3==2.6.3
 + wheel==0.46.3
 + xarray==2026.4.0

Step 5: Checking GitHub SSH access...
  GitHub SSH not configured. Setting up...
  GitHub SSH access verified.

Step 6: Installing QuakeCW packages from GitHub releases...
Using Python 3.12.13 environment at: /home01/x3336a02/.local/quakecw_venv
Resolved 4 packages in 825ms
Installed 1 package in 123ms
 + qcore==1.2 (from git+ssh://git@github.com/QuakeCW/qcore.git@1f46730b7e0222d17a6c0387d00bd9b9cd4d4da2)
Using Python 3.12.13 environment at: /home01/x3336a02/.local/quakecw_venv
Resolved 29 packages in 866ms
Installed 1 package in 106ms
 + im-calc==19.5.1 (from git+ssh://git@github.com/QuakeCW/IM_calculation.git@eeef40cd6094138545e8c44195da992cfdbcc0d3)
Using Python 3.12.13 environment at: /home01/x3336a02/.local/quakecw_venv
Resolved 3 packages in 813ms
Installed 1 package in 134ms
 + srf-generation==19.9.1 (from git+ssh://git@github.com/QuakeCW/Pre-processing.git@e51aaeb6c4bcd687c2621dd92aeb465db4214951)
Using Python 3.12.13 environment at: /home01/x3336a02/.local/quakecw_venv
    Updated ssh://git@github.com/QuakeCW/visualisation.git (e83db384324030746a085046ae876e4ac30dc880)
Resolved 2 packages in 12.65s
      Built visualization @ git+ssh://git@github.com/QuakeCW/visualisation.git@e83db384324030746a085046ae876e4ac30dc880
Prepared 1 package in 1.36s
Installed 1 package in 137ms
 + visualization==1.0.0 (from git+ssh://git@github.com/QuakeCW/visualisation.git@e83db384324030746a085046ae876e4ac30dc880)
Using Python 3.12.13 environment at: /home01/x3336a02/.local/quakecw_venv
    Updated ssh://git@github.com/QuakeCW/slurm_gm_workflow.git (71c47e13cbc3f3a9de2d3c71d0666441bf1dabe3)
Resolved 1 package in 7.21s
      Built workflow @ git+ssh://git@github.com/QuakeCW/slurm_gm_workflow.git@71c47e13cbc3f3a9de2d3c71d0666441bf1dabe3
Prepared 1 package in 3.39s
Installed 1 package in 369ms
 + workflow==21.11.1 (from git+ssh://git@github.com/QuakeCW/slurm_gm_workflow.git@71c47e13cbc3f3a9de2d3c71d0666441bf1dabe3)
...
...

Step 7: Updating .bashrc...
  Added sourcing to .bashrc
```

마지막 단계로 한반도 남부 속도모델을 다운 받을 것인지 묻는데, 45Gb에 달하는 큰 파일이므로 저장 용량이 충분하다면 Y를 누르도록 한다.
이 파일들은 모두 /scratch/<사용자 ID>로 다운받도록 되어 있으므로 저장 용량에는 큰 문제가 없을 것이다.
```
Step 8: Optional SouthKorea100m velocity model (45 GB)...
  This is a very large download and may take a long time.
  The model will be stored on scratch and symlinked from ~/project.
  Download SouthKorea100m velocity model? [y/N] y
  Downloading SouthKoreaVM100m.tar (45 GB) to scratch...
...
Length: 48380753920 (45G) [application/binary]
Saving to: '/scratch/x3336a02/SouthKoreaVM100m.tar'

100%[+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++===========>] 48,380,753,920 8.15MB/s   in 9m 54s 

2026-05-12 11:45:23 (11.2 MB/s) - '/scratch/x3336a02/SouthKoreaVM100m.tar' saved [48380753920/48380753920]

  Extracting SouthKoreaVM100m.tar to /scratch/x3336a02...
  Symlink created: /home01/x3336a02/project/cw/VelocityModel/3D/SouthKoreaVM100m -> /scratch/x3336a02/SouthKoreaVM100m

```

다운로드가 끝나면 압축을 풀어 정해진 곳에 설치를 하는 과정이 모두 자동으로 수행된다.

```
Step 9: Cleaning up archive files...
  Found archive files in /scratch/x3336a02:
    89M	/scratch/x3336a02/Velocity-Model_20260507.tar.gz
    46G	/scratch/x3336a02/SouthKoreaVM100m.tar
    425M	/scratch/x3336a02/quakecw_data_20260507.tar.gz
    256M	/scratch/x3336a02/project_local_20260507.tar.gz

  Delete these archive files to free up space? [y/N] y
  ✓ Archive files deleted.

Step 10: Optional cleanup of extracted source directories...
  Delete extracted source directories from scratch? (This will remove extracted files, keeping only final installed data) [y/N] m
  Skipping cleanup of extracted directories.

==============================================
Installation complete!

Please run: source ~/.bashrc
==============================================
```
위와 같은 인스톨 과정은 한번만 실행해주면 된다.

새로 만든 환경을 이용하려면 
```
source ~/.bashrc
```
을 실행하거나, 새로 로그인 하면 된다.

`$HOME/.bashrc` 가 아래와 비슷한 형태로 세팅되어 있도록 하자.
```
(quakecw_venv) x3336a02@login04: ~/project/cw/quakecw_workflow$ cat ~/.bashrc
# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions

export PROMPT='${debian_chroot:+($debian_chroot)}\u@\h: \w\$ '

PS1=$PROMPT

shopt -u progcomp
shopt -s direxpand

module load gcc/10.2.0 openmpi/3.1.0 craype-mic-knl libxc cmake netcdf

alias tree='find . | sed -e "s/[^-][^\/]*\// |/g" -e "s/|\([^ ]\)/|-\1/"'

# QuakeCW environment
source /home01/x3336a02/project/cw/quakecw_workflow/quakecw_config.sh
source "$VENV_DIR/bin/activate"

# Only on interactive shells, not PBS jobs
if [[ -z "$PBS_JOBID" ]]; then
    unset TMOUT
fi

```
위에서 `TMOUT`관련한 마지막 부분은 누리온에서 터미널을 일정시간 이상 사용하지 않았을 때에 자동으로 Timeout되어 SSH 연결이 끊어지는 현상을 방지하기 위함이다.
가장 중요한 부분은 `source /home01/x3336a02/project/cw/quakecw_workflow/quakecw_config.sh` 라인으로, 시뮬레이션에 필요한 모든 환경 변수들이 설정되어 있는 곳이다.

#### 실무책임자 계정


아래 내용은 새롭게 시스템을 구성할 경우에 참고할 것.

##### Python

```

$ export UV_INSTALL_DIR=/scratch/x3336a02/project/bin
curl -LsSf https://astral.sh/uv/install.sh | sh
downloading uv 0.11.7 x86_64-unknown-linux-gnu
installing to /scratch/x3336a02/project/bin
  uv
  uvx
everything's installed!
  
$ which uv  
/scratch/x3336a02/project/bin

$ cd $CW

[x3336a02@login01 cw]$ curl -LsSf https://astral.sh/uv/install.sh | sh
(python_env) [x3336a02@login01 cw]$ uv venv --python 3.12 python_env
Using CPython 3.12.13
Creating virtual environment at: python_env
Activate with: source python_env/bin/activate
(python_env) [x3336a02@login01 cw]$ source python_env/bin/activate
(python_env) [x3336a02@login01 cw]$ which python
/scratch/x3336a02/project/cw/python_env/bin/python
(python_env) [x3336a02@login01 cw]$ python --version
Python 3.12.13
```

##### EMOD3D 

2026년 4월 현재, 누리온에서 제공하는 FFTW패키지 (fftw_mpi/2.1.5 fftw_mpi/3.3.7)가 EMOD3D와 호환되지 않는 것으로 판단되어 FFTW를 별도로 빌드하도록 한다.

```
cd $HOME
wget http://www.fftw.org/fftw-3.3.10.tar.gz
tar -xzf fftw-3.3.10.tar.gz
cd fftw-3.3.10
./configure --prefix=$PROJECT/fftw --enable-float --enable-shared --enable-mpi CC=mpicc MPICC=mpicc F77=mpif77
make -j 8
make install
# Verify installation
ls -la $PROJECT/fftw/lib/ | grep fftw3f
```

EMOD3D를 다운받아 빌드
```
cd $PROJECT
git clone git@github.com:ucgmsim/EMOD3D.git
cd EMOD3D
mkdir build
cd build
cmake ../ -DFFTW3F_ROOT=$PROJECT/fftw -DCMAKE_PREFIX_PATH=$PROJECT/fftw
make -j 8
cd ../tools/
```
모든 것이 순조롭게 진행되었다면 아래와 같은 파일들을 볼수 있어야 함.
```
$ ls $PROJECT/EMOD3D/tools
emod3d-mpi_v3.0.13  emod3d-mpi_v3.0.8     generic_slip2srf  genslip_v5.4.2  hb_high_binmod_v5.4.5    hb_high_binmod_v6.0.3
emod3d-mpi_v3.0.4   fault_seg2gsf_dipdir  genslip_v3.3      genslip_v5.6.2  hb_high_binmod_v5.4.5.3  srf2stoch
```


