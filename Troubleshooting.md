# 워크플로우 사용 시 발생하는 상황에 대한 진단 및 대처법

### run_gmsim.sh이 죽은 (Killed) 경우

qstat을 사용해 확인해보니 아무것도 뜨지 않는데, check_status를 사용해보니, EMOD3D와 HF만 complete이고, merge_ts와 BB는 Queued상태이다.

screen -list를 사용해 run_gmsim.sh가 돌아가고 있던 screen 세션으로 다시 돌아가본다.

![PXL_20220509_021507694](https://user-images.githubusercontent.com/466989/167334973-35b8af04-1daa-4f94-bc3d-2e11b51cbf1e.jpg)


어떤 이유로 run_gmsim.sh가 죽어있음을 확인할 수 있다. 슈퍼컴퓨터가 때떄로 시스템 오류가 생기거나 정비를 할 때 이런 경우가 종종 목격된다.
![PXL_20220509_021959676](https://user-images.githubusercontent.com/466989/167334652-a8a8d00f-d3ef-44c2-bb62-6e0724f6bf2f.jpg)

대부분의 경우, 단순히 직전에 run_gmsim.sh을 실행할 때 명령어를 다시 입력해 주면 예전에 멈췄던 곳에서 이어받아 계산이 진행된다. 
run_gmsim.sh 실행시 사용했던 .yaml파일에 `n_max_retries`가 디폴트값으로 2가 설정되어 있는데, 이는 각각의 스텝에 문제가 생겨 제대로 complete가 되지 못했을 경우에 최대 몇번까지 재시도할 것인가를 설정한 것이다. 
이 경우에는 n_max_retries값으로 2가 부족함이 없으나, 혹 특정 스텝이 이전에 이미 2번 실패했다면 run_gmsim.sh을 재실행하기에 앞서 .yaml파일의 n_max_retries 값을 키워주도록 한다.

run_gmsim.sh를 재실행하고 check_status.py를 실행해보니 아래와 같이 출력되었다.
<img width="1315" alt="Screen Shot 2022-05-09 at 12 24 31 PM" src="https://user-images.githubusercontent.com/466989/167335460-0a4f07b8-8886-4659-a8ae-40d4ba2c786d.png">

run_gmsim.sh가 죽기전에 BB와 merge_ts가 queued상태였는데, 이것이 죽고 나서도 PBS 스케쥴러는 제출된 이 작업들을 제대로 처리했었음을 의미한다. 
다만, run_gmsim.sh이 죽어버려서 이 둘의 진행상태를 파악하지 못했기 때문에 제일 처음 check_status를 했을 때, merge_ts와 BB가 여전히 queued 상태로 떴던 것이다.



