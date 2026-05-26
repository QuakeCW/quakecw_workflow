
### Plot_ts

`sim_params.yaml`이 위치한 디렉토리에서 아래 명령어를 입력할 것.

```
(quakecw_venv) x3336a02@login01: /scratch/x3336a02/RunFolder/Pohang/Runs/Pohang/Pohang$ qsub -V $QUAKECW/scripts/run_plot_ts.pbs
```
실행이 되고 나면 `LF/OutBin`의 `*xtys.e3d` 파일들을 하나로 합치고, 매순간(timeslice) 마다 지진파의 분포지도를 그리게된다.

```
(quakecw_venv) x3336a02@login01: /scratch/x3336a02/RunFolder/Pohang/Runs/Pohang/Pohang$ tail -f ts.Pohang.22406622.log
it=604/610
it=605/610
it=606/610
it=607/610
it=608/610
it=609/610
Writing files took 70.367501 seconds (prep 13.439146 read 44.692623 gather 1.258677 write 10.934525 secs) 
Merge complete.
=== Plotting time series ===
Running plot_ts.py with 64 threads...
[[1.27545319e+02 3.73632965e+01 6.13145605e-02]
 [1.27550964e+02 3.73633614e+01 6.18836582e-02]
 [1.27556610e+02 3.73634300e+01 6.39565811e-02]
 ...
 [1.30291504e+02 3.37757339e+01 1.57828059e-03]
 [1.30296906e+02 3.37756729e+01 1.35130645e-03]
 [1.30302307e+02 3.37756157e+01 1.14335562e-03]]
0.0011433556
4.555232
========
psxy [WARNING]: Your plot (WxH = 16.00 x 9.00 inch) placed at (0.00, 0.00 inch) may exceed your PS_MEDIA (WxH = 16.00 x 9.00 inch)
mapproject [WARNING]: Your scale of 1 in -J was interpreted to mean 1:1 since no plotting is involved.
mapproject [WARNING]: If a scale of 1 was intended, please append a unit from c|i|p.
mapproject [ERROR]: Cannot specify map width with 1:xxxx format in -J option
....
timeslice 0238 completed in 35.85s
timeslice 0239 completed in 37.03s
timeslice 0432 completed in 37.20s
timeslice 0433 completed in 37.97s
timeslice 0434 completed in 37.12s
timeslice 0147 completed in 39.93s
timeslice 0148 completed in 39.77s
timeslice 0149 completed in 37.87s
timeslice 0264 completed in 34.44s
timeslice 0265 completed in 35.87s
timeslice 0266 completed in 37.44s
timeslice 0462 completed in 37.11s
timeslice 0463 completed in 38.79s
timeslice 0464 completed in 37.23s

SUCCESS: TS plots written to /scratch/x3336a02/RunFolder/Pohang/Runs/Pohang/Pohang/plots/ts_Pohang


```
`GMT`의 특성상 경고나 에러 메시지가 많이 뜰수 있으나 심각한 오류가 아니므로 인스톨 과정이나 시뮬레이션 과정에서 문제가 없었다면 비디오 파일을 생성할 것이다.

*아래의 내용은 코드를 테스트해가며 메뉴얼이 업데이트되어야 함.*

### [고난이도] 복수의 시뮬레이션 결과와 관측값 비교

하나의 이벤트에 대해 복수의 시뮬레이션 결과가 있는 경우, gmsim_plot.py에 한번 이상의 --gmsim_yaml을 추가하면 된다.
예를 살펴보도록 하겠다.

아래의 `Busan_Data/Sample_runs`라는 디렉토리에 경주와 포항 지진을 각각 sdrop을 바꿔가며 두 번씩 계산한 시뮬레이션 결과 데이터가 저장되어 있다.

```
(python3_nurion) x2568a02@login02:/scratch/x2568a02/CWNU/quakecw_workflow/RunFolder/Pohang> ls /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/

Gyeongju_20220422_sdrop100  Gyeongju_20220422_sdrop50  Pohang_20220422_sdrop20  Pohang_20220422_sdrop50
```

두 가지 포항 시뮬레이션을 관측 데이터와 비교해보도록 하겠다. `/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/`으로 이동하자. 이 두 시뮬레이션의 gmsim.yaml 파일을 찾아보자.

```
(python3_nurion) x2568a02@login02:/scratch/x2568a02/CWNU/Busan_Data/Sample_runs> find . -name "gmsim*.yaml"
./Pohang_20220422_sdrop20/gmsim_Pohang_20220422_sdrop20.yaml
./Pohang_20220422_sdrop50/gmsim_Pohang_20220422_sdrop50.yaml
```
그리고 그 내용을 살펴보자.

```
(python3_nurion) x2568a02@login02:/scratch/x2568a02/CWNU/Busan_Data/Sample_runs> cat ./Pohang_20220422_sdrop20/gmsim_Pohang_20220422_sdrop20.yaml
workflow: /scratch/x2568a02/gmsim_home/Environments/v211213/workflow
sim_root_dir: /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20
fault_name: Pohang

(python3_nurion) x2568a02@login02:/scratch/x2568a02/CWNU/Busan_Data/Sample_runs> cat ./Pohang_20220422_sdrop50/gmsim_Pohang_20220422_sdrop50.yaml
workflow: /scratch/x2568a02/gmsim_home/Environments/v211213/workflow
sim_root_dir: /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50
fault_name: Pohang
```
위에서 시뮬레이션을 하기 위해 만들었던 gmsim.yaml에는 이것보다 더 많은 정보들 (예: 단층모델,속도모델, 관측소 관련 정보)이 저장되어 있었던 것을 기억할 것이다. 사실 시각화 단계에서는 이 세가지만 정보만 있으면 충분하다. 때때로 시각화를 하려고 하는데 사뮬레이션에 사용했던 gmsim.yaml를 찾지 못할 수도 있다. 그럴 때면, 이렇게 세 가지 정보만 포함된 간단한 .yaml파일을 작성해서 사용하면 된다.

`cd` 명령어로 원래 Pohang 디렉토리로 돌아가자.
```
(python3_nurion) x2568a02@login02:/scratch/x2568a02/CWNU/quakecw_workflow/RunFolder/Pohang> cp /scratch/x2568a02/CWNU/Busan_Data/Sample_runs//Pohang_20220422_sdrop20/gmsim_Pohang_20220422_sdrop20.yaml .
(python3_nurion) x2568a02@login02:/scratch/x2568a02/CWNU/quakecw_workflow/RunFolder/Pohang> cp /scratch/x2568a02/CWNU/Busan_Data/Sample_runs//Pohang_20220422_sdrop50/gmsim_Pohang_20220422_sdrop50.yaml .
```

`nano`를 사용해 두 파일의 `workflow`부분을 고쳐주자. `x2568a02`를 자신의 계정으로 수정해서 저장하도록 한다. 

아래 명령어를 사용해 실행시켜보자. --outdir라는 옵션은 그림 파일들을 저장할 위치를 가리킨다. 특정 위치를 사용하지 않으면 자동으로 plots라는 디렉토리를 만들어 저장한다.

```
(python3_nurion) x2568a02@login02:/scratch/x2568a02/CWNU/quakecw_workflow/RunFolder/Pohang>  python $QUAKECW/analysis/gmsim_plots.py --gmsim_yaml ./gmsim_Pohang_20220422_sdrop20.yaml --gmsim_yaml ./gmsim_Pohang_20220422_sdrop50.yaml --obs /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang --outdir plots_Pohang_20220422
##### Observation data: /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang
##### Sim BB (Acc) 1: ('Pohang_20220422_sdrop20', '/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20/Runs/Pohang/Pohang/BB/Acc/BB.bin')
##### Sim BB (Acc) 2: ('Pohang_20220422_sdrop50', '/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50/Runs/Pohang/Pohang/BB/Acc/BB.bin')
##### IM CSV 1: ('Pohang_20220422_sdrop20', '/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20/Runs/Pohang/Pohang/IM_calc/Pohang.csv')
##### IM CSV 2: ('Pohang_20220422_sdrop50', '/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50/Runs/Pohang/Pohang/IM_calc/Pohang.csv')
##### IM Plots 1: ('Pohang_20220422_sdrop20', '/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20/Runs/Pohang/Pohang/verification/IM_plot/geom/non_uniform_im')
##### IM Plots 2: ('Pohang_20220422_sdrop50', '/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50/Runs/Pohang/Pohang/verification/IM_plot/geom/non_uniform_im')
##### Stations extracted from Observation data
##### Station list: ADO2 AJD BBK BGD BRN BRS CGD CHS CIGB DAG2 DKJ EURB EUSB GRE GSU GUWB HACA HAK HCNA HDB HKU HSB HWSB JINA JJB JRB JSB KCH2 KJM KMC KRN KSA KUJA MAK MGB MIYA MKL MRD MUN NPR PCH PHA2 RWD SACA SND SNU TJN TOY2 UCN WID WSN YGN YIN YKB YOCB YPD YSB



##### Start Plotting
python /scratch/x2568a02/gmsim_home/Environments/v211213/visualization/waveform/waveforms.py --waveforms /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_Acc Obs --waveforms /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20/Runs/Pohang/Pohang/BB/Acc/BB.bin Sim -t 90 --acc --no-amp-normalize --stations ADO2 AJD BBK BGD BRN BRS CGD CHS CIGB DAG2 DKJ EURB EUSB GRE GSU GUWB HACA HAK HCNA HDB HKU HSB HWSB JINA JJB JRB JSB KCH2 KJM KMC KRN KSA KUJA MAK MGB MIYA MKL MRD MUN NPR PCH PHA2 RWD SACA SND SNU TJN TOY2 UCN WID WSN YGN YIN YKB YOCB YPD YSB --out plots_Pohang_20220422/waveforms_acc_Pohang_20220422_sdrop20

python /scratch/x2568a02/gmsim_home/Environments/v211213/visualization/waveform/waveforms.py --waveforms /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_Vel Obs --waveforms /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20/Runs/Pohang/Pohang/BB/Acc/BB.bin Sim -t 90 --no-amp-normalize --stations ADO2 AJD BBK BGD BRN BRS CGD CHS CIGB DAG2 DKJ EURB EUSB GRE GSU GUWB HACA HAK HCNA HDB HKU HSB HWSB JINA JJB JRB JSB KCH2 KJM KMC KRN KSA KUJA MAK MGB MIYA MKL MRD MUN NPR PCH PHA2 RWD SACA SND SNU TJN TOY2 UCN WID WSN YGN YIN YKB YOCB YPD YSB --out plots_Pohang_20220422/waveforms_vel_Pohang_20220422_sdrop20


python /scratch/x2568a02/gmsim_home/Environments/v211213/visualization/waveform/waveforms.py --waveforms /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_Acc Obs --waveforms /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50/Runs/Pohang/Pohang/BB/Acc/BB.bin Sim -t 90 --acc --no-amp-normalize --stations ADO2 AJD BBK BGD BRN BRS CGD CHS CIGB DAG2 DKJ EURB EUSB GRE GSU GUWB HACA HAK HCNA HDB HKU HSB HWSB JINA JJB JRB JSB KCH2 KJM KMC KRN KSA KUJA MAK MGB MIYA MKL MRD MUN NPR PCH PHA2 RWD SACA SND SNU TJN TOY2 UCN WID WSN YGN YIN YKB YOCB YPD YSB --out plots_Pohang_20220422/waveforms_acc_Pohang_20220422_sdrop50


python /scratch/x2568a02/gmsim_home/Environments/v211213/visualization/waveform/waveforms.py --waveforms /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_Vel Obs --waveforms /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50/Runs/Pohang/Pohang/BB/Acc/BB.bin Sim -t 90 --no-amp-normalize --stations ADO2 AJD BBK BGD BRN BRS CGD CHS CIGB DAG2 DKJ EURB EUSB GRE GSU GUWB HACA HAK HCNA HDB HKU HSB HWSB JINA JJB JRB JSB KCH2 KJM KMC KRN KSA KUJA MAK MGB MIYA MKL MRD MUN NPR PCH PHA2 RWD SACA SND SNU TJN TOY2 UCN WID WSN YGN YIN YKB YOCB YPD YSB --out plots_Pohang_20220422/waveforms_vel_Pohang_20220422_sdrop50


['/scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv']
python /scratch/x2568a02/gmsim_home/Environments/v211213/visualization/im/psa_comparisons.py --run-name Pohang_20220422_sdrop20 --stations ADO2 AJD BBK BGD BRN BRS CGD CHS CIGB DAG2 DKJ EURB EUSB GRE GSU GUWB HACA HAK HCNA HDB HKU HSB HWSB JINA JJB JRB JSB KCH2 KJM KMC KRN KSA KUJA MAK MGB MIYA MKL MRD MUN NPR PCH PHA2 RWD SACA SND SNU TJN TOY2 UCN WID WSN YGN YIN YKB YOCB YPD YSB --imcsv /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20/Runs/Pohang/Pohang/IM_calc/Pohang.csv Sim --imcsv /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv Obs -d plots_Pohang_20220422/psa_comparisons_Pohang_20220422_sdrop20
b"['/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20/Runs/Pohang/Pohang/IM_calc/Pohang.csv', 'Sim']\n['/scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv', 'Obs']\n"
['/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20/Runs/Pohang/Pohang/IM_calc/Pohang.csv', 'Sim']
['/scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv', 'Obs']


['/scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv']
python /scratch/x2568a02/gmsim_home/Environments/v211213/visualization/im/psa_comparisons.py --run-name Pohang_20220422_sdrop50 --stations ADO2 AJD BBK BGD BRN BRS CGD CHS CIGB DAG2 DKJ EURB EUSB GRE GSU GUWB HACA HAK HCNA HDB HKU HSB HWSB JINA JJB JRB JSB KCH2 KJM KMC KRN KSA KUJA MAK MGB MIYA MKL MRD MUN NPR PCH PHA2 RWD SACA SND SNU TJN TOY2 UCN WID WSN YGN YIN YKB YOCB YPD YSB --imcsv /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50/Runs/Pohang/Pohang/IM_calc/Pohang.csv Sim --imcsv /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv Obs -d plots_Pohang_20220422/psa_comparisons_Pohang_20220422_sdrop50
b"['/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50/Runs/Pohang/Pohang/IM_calc/Pohang.csv', 'Sim']\n['/scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv', 'Obs']\n"
['/scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50/Runs/Pohang/Pohang/IM_calc/Pohang.csv', 'Sim']
['/scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv', 'Obs']


['/scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv']
python /scratch/x2568a02/gmsim_home/Environments/v211213/visualization/im/psa_bias.py --run_name Pohang_20220422_sdrop20 --imcsv /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop20/Runs/Pohang/Pohang/IM_calc/Pohang.csv Sim --imcsv /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv Obs -o plots_Pohang_20220422/psa_bias_Pohang_20220422_sdrop20


['/scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv']
python /scratch/x2568a02/gmsim_home/Environments/v211213/visualization/im/psa_bias.py --run_name Pohang_20220422_sdrop50 --imcsv /scratch/x2568a02/CWNU/Busan_Data/Sample_runs/Pohang_20220422_sdrop50/Runs/Pohang/Pohang/IM_calc/Pohang.csv Sim --imcsv /scratch/x2568a02/CWNU/Busan_Data/Data/Obs/Obs_20220511/Pohang/Obs_IM/Pohang.csv Obs -o plots_Pohang_20220422/psa_bias_Pohang_20220422_sdrop50


plots_Pohang_20220422/im_plots_Pohang_20220422_sdrop20
plots_Pohang_20220422/im_plots_Pohang_20220422_sdrop50


##### All complete: Check plots_Pohang_20220422
```

지정한 디렉토리로 가서 확인해보자.

```
(python3_nurion) x2568a02@login02:/scratch/x2568a02/CWNU/quakecw_workflow/RunFolder/Pohang> cd plots_Pohang_20220422
(python3_nurion) x2568a02@login02:/scratch/x2568a02/CWNU/quakecw_workflow/RunFolder/Pohang/plots_Pohang_20220422> ls
im_plots_Pohang_20220422_sdrop20  psa_bias_Pohang_20220422_sdrop50         waveforms_acc_Pohang_20220422_sdrop20  waveforms_vel_Pohang_20220422_sdrop50
im_plots_Pohang_20220422_sdrop50  psa_comparisons_Pohang_20220422_sdrop20  waveforms_acc_Pohang_20220422_sdrop50
psa_bias_Pohang_20220422_sdrop20  psa_comparisons_Pohang_20220422_sdrop50  waveforms_vel_Pohang_20220422_sdrop20
```



### [참고] IM_plot 

자동으로 계산되므로 특별히 알아야 할 필요는 없지만, 참고로 IM_plot하는 단계를 설명하겠다.

IM_Calculation단계를 거쳐야 함.시뮬레이션 디렉토리에서 IM_calc디렉토리에 \*.csv파일이 존재하는 지 확인할 것.
IM Calculation 결과와 관측점의 위도/경도를 매칭해서 xyz파일을 생성해낸다.
IM_calc의 parent 디렉토리 (LF,HF,BB등이 있는 곳)로 가서 아래를 실행시킴

```

FAULT=Pohang
REL=Pohang
python $gmsim/visualization/im/spatialise_im.py IM_calc/${REL}.csv ../fd_rt01-h0.100.ll -o plot
```

위에서 non_uniform_im.xyz파일이 plot이라는 디렉토리에 생성되었을 것임. 아울러 im_order.txt라는 파일도 생겨나는데, 계산된 IM들의 순서가 기록된 파일임.

  
plot 디렉토리에 가서 아래 명령어를 입력. FAULT와 REL을 위처럼 변수로 지정해주면 다른 시뮬레이션 결과값에 대응할 수 있다.  
  

```
cd plot
python $gmsim/visualization/sources/plot_items.py -c ../../../../Data/Sources/${FAULT}/Srf/${REL}.srf --xyz non_uniform_im.xyz -t ${FAULT} --xyz-cpt-label `cat im_order.txt` -f ${FAULT} --xyz-landmask --xyz-cpt hot --xyz-transparency 30 --xyz-grid --xyz-grid-contours --xyz-grid-search 12m --xyz-size 1k --xyz-cpt-invert --xyz-model-params ../../../../Data/VMs/${FAULT}/model_params_rt01-h0.100 -n 4
```
  

