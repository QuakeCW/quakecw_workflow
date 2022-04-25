# Running quakecw_workflow as a Docker Image
CWNU Earthquake Research Group's Adaptation of QuakeCoRE NZ workflow

Korean Ground Motion Simulation @ Nurion

배성은(University of Canterbury, QuakeCoRE 소프트웨어 팀장 / 창원대학교 BP Fellow)

# 도커 허브

```
docker pull glorykingsman/quakekorea
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

