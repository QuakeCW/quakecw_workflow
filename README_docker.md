# Running quakecw_workflow as a Docker Image
CWNU Earthquake Research Group's Adaptation of QuakeCoRE NZ workflow

Korean Ground Motion Simulation @ Nurion

배성은(University of Canterbury, QuakeCoRE 소프트웨어 팀장 / 창원대학교 BP Fellow)

# 도커 허브

```
docker pull glorykingsman/quakekorea
```

[1] 종종 도커허브가 Permission Denied같은 에러를 일으키는 경우 (특히 `docker push`시) `docker login -u 사용자ID -p 비밀번호` 명령어를 사용해 도커허브에서 허용한 collaborator 계정으로 다시 로그인해줘야 함.
리눅스에서 `docker info`같은 기본적인 명령어가 퍼미션 에러를 일으키는 경우, docker 그룹에 현재 사용자가 포함되어 있나 확인할 것
```
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


# 도커 컨테이너 시작

```
./dockerun.bat
```


혹은

```
./docker run -it 
```


이 때 QuakeData는 로컬 컴퓨터의 디렉토리로 도커 컨테이너로부터 액세스가 가능하도록 마운트한다.

