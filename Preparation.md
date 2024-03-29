# 창원대 지진공학 및 방재 연구실 학생들을 위한 누리온/리눅스 워크스테이션 셋업 안내

## ssh
리눅스에서 누리온에서 손쉽게 접근하기 위해서 아래 셋업을 권장함. 한번만 시행하면 됨.

`nano ~/.ssh/config`

아래 내용을 집어넣고 User 항목에 자신의 로그인 어카운트 (예: x2568a02) 를 넣어준다.
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
(x2568a02@150.183.150.12) Password(OTP):
(x2568a02@150.183.150.12) Password:
Last failed login: Mon May  2 15:29:22 KST 2022 from 1.219.251.31 on ssh:notty
There were 10 failed login attempts since the last successful login.
Last login: Sun May  1 20:35:13 2022 from 161.202.72.155
================ KISTI 5th NURION System ====================
 * Any unauthorized attempts to use/access the system can be
   investigated and prosecuted by the related Act
   (THE PROTECTION OF INFORMATION AND COMMUNICATIONS INFRASTRUCTURE)
....

x2568a02@login02:~>
```

`ssh nurion`이라고 하면 로그인 노드 1번부터 4번 중 하나가 자동 배정되며, `ssh nurion1...4`는 로그인 노드의 하나를 특정해서 접속할 수 있다. 시뮬레이션을 돌릴 때, 특정 노드를 지정하는 것이 편리할 때가 있음.

## 누리온 사용환경 설정

다음은 배성은 (x2568a02)가 구축해 놓은 시뮬레이션 환경을 사용하기 위한 설정이다.

누리온에 로그인해서 ~/.bashrc를 수정한다.

```
nano ~/.bashrc
```

아래 내용을 제일 밑바닥에 추가하도록 하자.

```
# User specific aliases and functions
export PS1='${debian_chroot:+($debian_chroot)}\u@\h: \w> '
shopt -u progcomp

alias bash="/bin/bash"
export ADMIN=x2568a02
export MMBATCH=b1
export CWSCRATCH=/scratch/$ADMIN/users
export MYSCRATCH=/scratch/$ADMIN/users/$USER

export ENV=$HOME/gmsim/Environments/v211213/
alias tree='find . | sed -e "s/[^-][^\/]*\// |/g" -e "s/|\([^ ]\)/|-\1/"'
alias act_env='activate_env $ENV'

export SCRATCH=/scratch/$ADMIN
source $SCRATCH/gmsim_home/share/bashrc.uceq

export PATH=$PATH:$SCRATCH/gmsim_home/Environments/nurion/virt_envs/python3_nurion/bin
#export PATH=$PATH:$SCRATCH/gmsim_home/gmsim/Environments/nurion/ROOT/local/gnu/bin:$SCRATCH/gmsim_home/pkg/tar/ffmpeg-4.2.2-amd64-static
QUAKECW=$SCRATCH/CWNU/quakecw_workflow
```

저장하고 `source`명령어를 실행하면 고친 내용이 로딩된다. (다음번 누리온에 로그인하면 자동으로 로딩됨)
```
x2568a02@login02:~> source ~/.bashrc
```

### 프로그램 패키지 인스톨

자기 홈 디렉토리로 간다.

```
cd ~/
```
만약 예전에 사용하던 `gmsim` 디렉토리가 있다면 백업하도록 한다. (테스트 후에 삭제해도 됨)

```
mv gmsim gmsim.backup
```

배성은 (x2568a02)이 2022/05/02 제작한 셋업을 공유해 사용하기로 한다. 

```
ln -sf /scratch/x2568a02/gmsim_home gmsim
```


제대로 로딩되었는지 확인하려면 `act_env` 명령어를 실행해본다. Activate Environment라는 의미를 가진 단축키 (alias)로 `~/.bashrc` 제일 아래에 지정한 내용이다.

```
x2568a02@login02:~> act_env

 	'gcc/8.3.0' supports the following modules

	{MPI}
	'mvapich2/2.3.1' 'mvapich2/2.3.6' 'openmpi/3.1.0'

	{cpu_types}
	'craype-mic-knl' 'craype-x86-skylake'

	{libraries}
	'CDO/1.8.2' 'hdf4/4.2.13' 'hdf5/1.10.2' 'lapack/3.7.0' 'libxc/4.0.0' 'libxc/4.3.4' 'NCO/4.7.4' 'NCO/4.9.2' 'ncl/6.5.0' 'ncview/2.1.7' 'netcdf/4.6.1'

(python3_nurion) x2568a02@login02:~>
```
실행시 출력되는 내용은 무시해도 무방.

터미널의 프롬프트가 `(python3_nurion) x2568a02@login02:~>` 모양으로 바뀌었으면 설정이 잘 되었음을 의미함.

마지막으로 `CWSCRATCH` 디렉토리 (`/scratch/x2568a02/users`)에 `$MYSCRATCH` 디렉토리를 만들어주자.

```
x2568a02@login02:/scratch/x2568a02/users> mkdir $USER
```

$MYSCRATCH로 이동해간다.
```
x2568a02@login02:/scratch/x2568a02/users> cd $MYSCRATCH
x2568a02@login02:/scratch/x2568a02/users/x2568a02>
```

이 곳을 대부분의 작업을 하는 장소로 사용하도록 할 것.


```
cd ~/
ln -sf /scratch/x2568a02/users/baes/Velocity-Model
ln -sf /scratch/x2568a02/users/baes/VM_KVM

```

`ls -al`해서 아래와 같은 라인이 보이면 잘되었음을 의미한다.
```
lrwxrwxrwx    1 x2568a02 rd0862       43 Jan 10 12:34 Velocity-Model -> /scratch/x2568a02/users/baes/Velocity-Model
lrwxrwxrwx    1 x2568a02 rd0862       35 Jan 10 12:35 VM_KVM -> /scratch/x2568a02/users/baes/VM_KVM

```


### 참고: gmsim 패키지에서 문제가 생겼을 경우
gmsim 패키지를 만드는 과정에서 사용자 로그인 아이디 x2568a02가 하드코딩되어 퍼미션 관련한 문제가 생겨날 수 있는데, 이같은 경우 문의바람.
