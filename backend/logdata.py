import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# 현재 파일의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# 절대 경로로 파일 읽기
df1 = pd.read_csv(os.path.join(current_dir, "../settop_0527.csv"), index_col=0)
df2 = pd.read_csv(os.path.join(current_dir, "../settop.csv"), index_col=0)

logData = []

@app.get("/api/current_time")
async def get_current_time():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return JSONResponse(content={'current_time': current_time})

@app.get("/api/data/{device_id}")
async def get_device_data(device_id: str):
    data = [entry for entry in logData if entry['group'] == device_id]
    return JSONResponse(content=data)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# FastAPI 서버 주소
server_url = "http://localhost:5000/api/log"

def log_random_samples_by_group(df, group_column, columns, start_time, interval_minutes, iterations=1000):
    global logData
    logData = []
    current_time = start_time
    for i in range(iterations):
        log_entries = []
        for group_name, group_df in df.groupby(group_column):
            random_samples = {column: np.random.choice(group_df[column].dropna().values) for column in columns}
            log_entries.append({
                "measurement_time": current_time.strftime('%Y-%m-%d %H:%M:%S'),
                "group": group_name,
                "random_samples": random_samples
            })

        # 모든 그룹에 대한 로그를 동시에 출력 및 서버로 전송
        for entry in log_entries:
            logger.info(entry)
            logData.append(entry)
            try:
                response = requests.post(server_url, json=entry)
                if response.status_code != 200:
                    logger.error(f"Failed to send data to server: {response.status_code}")
            except Exception as e:
                logger.error(f"Exception occurred: {str(e)}")
        
        # 10분 후로 시간 증가
        current_time += timedelta(minutes=interval_minutes)
        
        # 잠시 대기 (실제 실행 중에는 이 부분을 주석 처리할 수 있습니다)
        time.sleep(0.1)

# 로그 기록 시작 시간 및 간격 설정
start_time = datetime(2023, 5, 1, 0, 0)
interval_minutes = 10

# 로그 기록 시작
log_random_samples_by_group(df1, 'cell_number', ['upper_power2', 'upper_snr', 'lower_power', 'lower_snr'], start_time, interval_minutes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)

