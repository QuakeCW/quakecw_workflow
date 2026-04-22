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


다음은 배성은 (x2568a02)가 구축해 놓은 시뮬레이션 환경을 사용하기 위한 설정이다.

누리온에 로그인해서 ~/.bashrc를 수정한다.

```
nano ~/.bashrc
```

아래 내용을 제일 밑바닥에 추가하도록 하자.

```
# User specific aliases and functions
export PS1='${debian_chroot:+($debian_chroot)}\u@\h: \w> '
# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
shopt -u progcomp
shopt -s direxpand
unset TMOUT # disable auto-timeout

export ADMIN=x3336a02
export SCRATCH=/scratch/$ADMIN
export PROJECT=$SCRATCH/project
export MYSCRATCH=$SCRATCH/users/$USER
export CW=$PROJECT/cw
export UC=$PROJECT/uc
export QUAKECW=$CW/quakecw_workflow
export gmsim=$CW

export GMT_DIR=$PROJECT/local/gmt
export GMT_DATADIR=$GMT_DIR/share
export HDF5_DIR=$PROJECT/local/hdf5
export LD_LIBRARY_PATH=$PROJECT/local/fftw/lib:$PROJECT/local/OpenBLAS/lib:$HDF5_DIR/lib:$PROJECT/local/spatialindex/lib:$GMT_DIR/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=$PROJECT/local/fftw/lib/pkgconfig:$PROJECT/local/OpenBlas/lib/pkgconfig:$PKG_CONFIG_PATH
export UV_CACHE_DIR=$SCRATCH/.cache/uv

module load gcc/10.2.0 openmpi/3.1.0 craype-mic-knl libxc cmake netcdf

alias act_cw_env="source $CW/python_env/bin/activate"
act_cw_env

export PATexport PYTHONPATH=$gmsim/Pre-processing:$PYTHONPATH
export PATH=$PROJECT/bin:$PROJECT/EMOD3D/tools:$GMT_DIR/bin:$PATH

alias tree='find . | sed -e "s/[^-][^\/]*\// |/g" -e "s/|\([^ ]\)/|-\1/"'


```

저장하고 `source`명령어를 실행하면 고친 내용이 로딩된다. (다음번 누리온에 로그인하면 자동으로 로딩됨)
```
x2568a02@login02:~> source ~/.bashrc
```

### 프로그램 패키지 인스톨

#### 실무책임자 계정
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

#### 기타 사용자 계정

```
cd ~/
```
만약 예전에 사용하던 `gmsim` 디렉토리가 있다면 백업하도록 한다. (테스트 후에 삭제해도 됨)

```
mv gmsim gmsim.backup
```

배성은 (x3336a02)이 2022/05/02 제작한 셋업을 공유해 사용하기로 한다. 

```
ln -sf /scratch/x3336a02/gmsim_home gmsim
```


제대로 로딩되었는지 확인하려면 `act_cw_env` 명령어를 실행해본다. Activate Environment라는 의미를 가진 단축키 (alias)로 `~/.bashrc` 제일 아래에 지정한 내용이다.

```
[x3336a02@login01 project]$ act_cw_env
(python_env) [x3336a02@login01 project]$ which python
/scratch/x3336a02/project/cw/python_env/bin/python
```

터미널의 프롬프트가 `(python_env) [x3336a02@....]$` 모양으로 바뀌었으면 설정이 잘 되었음을 의미함.

마지막으로 $SCRATCH/users에 `$USER`이름의 디렉토리를 만들어주자.

```
(python_env) [x3336a02@login01 users]$ mkdir -p $USER
(python_env) [x3336a02@login01 users]$ ls
x3336a02

```

$MYSCRATCH로 이동해간다.
```
(python_env) [x3336a02@login01 users]$ cd $MYSCRATCH
(python_env) [x3336a02@login01 x3336a02]$ pwd
/scratch/x3336a02/users/x3336a02

```

이 곳을 대부분의 작업을 하는 장소로 사용하도록 할 것. 끝으로 `Velocity-Model` 심볼릭 링크를 홈디렉토리에 만들어주자.


```
cd ~/
ln -sf /scratch/x3336a02/project/cw/Velocity-Model

```

`ls -al`해서 아래와 같은 라인이 보이면 잘되었음을 의미한다.
```
lrwxrwxrwx    1 x3336a02 rd0862       43 Jan 10 12:34 Velocity-Model -> /scratch/x3336a02/project/cw/Velocity-Model

```


### 참고: gmsim 패키지에서 문제가 생겼을 경우
gmsim 패키지를 만드는 과정에서 사용자 로그인 아이디 x3336a02 하드코딩되어 퍼미션 관련한 문제가 생겨날 수 있는데, 이같은 경우 문의바람.
