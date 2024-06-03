import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time
import requests
from flask import Flask, jsonify

app = Flask(__name__)

df1 = pd.read_csv("../settop_0527.csv", index_col=0)   # 경로 수정
df2 = pd.read_csv("../settop.csv", index_col=0)   # 경로 수정

@app.route('/api/current_time', methods=['GET'])
def get_current_time():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return jsonify({'current_time': current_time})

@app.route('/api/data/<device_id>', methods=['GET'])
def get_device_data(device_id):
    data = [entry for entry in logData if entry['group'] == device_id]
    return jsonify(data)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Flask 서버 주소
server_url = "http://localhost:5000/api/log"

logData = []

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

if __name__ == '__main__':
    app.run(port=5001)
