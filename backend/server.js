const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const http = require('http');
const WebSocket = require('ws');
const fetch = require('node-fetch'); // node-fetch 모듈 추가
const app = express();
const port = 5000;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '../frontend')));

let logData = [];

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// API 엔드포인트: 로그 데이터 수신
app.post('/api/log', (req, res) => {
  const { group, random_samples, measurement_time } = req.body;
  logData.push({ group, random_samples, measurement_time });

  // 웹소켓을 통해 실시간 데이터 전송
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({ group, random_samples, measurement_time }));
    }
  });

  res.sendStatus(200);
});

// API 엔드포인트: 특정 셀 번호에 대한 데이터 가져오기
app.get('/api/data/:cellNumber', async (req, res) => {
  const cellNumber = req.params.cellNumber;
  try {
    const response = await fetch(`http://localhost:5001/api/data/${cellNumber}`);
    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.statusText}`);
    }
    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

server.listen(port, '0.0.0.0', () => {
  console.log(`서버가 http://0.0.0.0:${port} 에서 실행 중입니다.`);
});


