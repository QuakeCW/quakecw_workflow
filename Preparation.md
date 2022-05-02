# 창원대 지진공학 및 방재 연구실 학생들을 위한 누리온/리눅스 워크스테이션 셋업 안내

## ssh
리눅스에서 누리온에서 손쉽게 접근하기 위해서 아래 셋업을 권장함. 한번만 시행하면 됨.

`nano ~/.ssh/config`

아래 내용을 집어넣고 User 항목에 자신의 유저 어카운트를 넣어준다.
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
	User 유저어카운트
    Hostname 150.183.150.11
Host nurion2
	User 유저어카운트
    Hostname 150.183.150.12
Host nurion3
	User 유저어카운트
    Hostname 150.183.150.13
Host nurion4
	User 유저어카운트
    Hostname 150.183.150.14
Host nurion
	User 유저어카운트
	Hostname nurion.ksc.re.kr
Host nurion-dm
	User 유저어카운트
	Hostname nurion-dm.ksc.re.kr
```

그리고, `~/.ssh` 아래에 `sockets` 라는 디렉토리를 생성

`mkdir ~/.ssh/sockets`