# 프로젝트 이름
#### 데이터 설명
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

#### K-means 알고리즘을 이용한 추천

3개의 군집(최고속도, 배터리성능, 충전속도)으로 분류.

군집 형성 전 아래와 같이 각각의 점수를 계산.
1 최고속도 60 가속(제로백) 40 가중치적용하여
속도점수 계산

2 배터리용량40 주행거리40 배터리효율성20
배터리 성능점수 계산

3 급속충전출력80 배터리용량20
충전속도 점수 계산

위 점수를 기반으로 상위 33% 데이터를 추린 후 클러스터링 수행
그리고 추천
![image](https://cdn.prod.website-files.com/5f1008192dda2baf6f4e16c3/60ab5871a7fd8d9b4f013185_behind%20the%20algorithm_user%20clustering.png)

#### 구동방식

streamlit


