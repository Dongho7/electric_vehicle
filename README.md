# **Find Optimal Electric Vehicle**  

## 데이터 설명
![image](https://postfiles.pstatic.net/MjAyNTA3MTdfNjUg/MDAxNzUyNzM5MDQ5NjA3.LWF6kUQQEAyK4zfA63YNGbAIVvl98t7gktGsT_RiKQYg.Zhj-luAmPsikNebXUe_1UvyN6mNpAZuba6E0jcW2RwEg.PNG/%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%85%8B%EC%84%A4%EB%AA%85.png?type=w773)
```python
df.shape # (478, 22)
raw_df.columns
# Index(['brand', 'model', 'top_speed_kmh', 'battery_capacity_kWh',
#        'battery_type', 'number_of_cells', 'torque_nm', 'efficiency_wh_per_km',
#        'range_km', 'acceleration_0_100_s', 'fast_charging_power_kw_dc',
#        'fast_charge_port', 'towing_capacity_kg', 'cargo_volume_l', 'seats',
#        'drivetrain', 'segment', 'length_mm', 'width_mm', 'height_mm',
#        'car_body_type', 'source_url'],
#       dtype='object')
```
![image](https://postfiles.pstatic.net/MjAyNTA3MTdfMjU1/MDAxNzUyNzM5NTMwMTM3._k8jbd0n1IH32o3uS2LCPL8IGYHkZgwvrKurX_UpXpgg.5yOhHt7qSLrGRvy_-2WvxwHkzsKWPp1kZzFbxC4uduQg.PNG/corr.png?type=w773)
---
## K-means 알고리즘을 이용한 추천  

![image](https://cdn.prod.website-files.com/5f1008192dda2baf6f4e16c3/60ab5871a7fd8d9b4f013185_behind%20the%20algorithm_user%20clustering.png)

3개의 군집(최고속도, 배터리성능, 충전속도)으로 분류.  
군집 형성 전 아래와 같이 각각의 점수를 계산.  
1 최고속도 40 가속(제로백) 60 가중치적용하여 속도점수 계산  

2 배터리용량30 주행거리30 배터리효율성40 배터리 성능점수 계산  

3 급속충전출력90 배터리용량10 충전속도 점수 계산  
  
각 분야별 상위 30%임계값을 계산 후 각 차량별로 임계값을 넘는 분야 확인  
  
클러스터링분류 규칙적용
- 임계값을 넘지못하면, 3개 점수 중 가장 높은 분야로 강제 배정  
- 임계값을 넘으면, 그 중 가장 높은 점수의 분야로 분류  
  
그리고 TOP5 모델 선정 추천.

---
## 구동방식
[streamlit](https://electricvehicle-rkzpnw8ur6hpnl5ythsdrd.streamlit.app/)
