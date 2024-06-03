const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const http = require('http');
const WebSocket = require('ws');
const { spawn } = require('child_process');
const app = express();
const port = 5000;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '../frontend')));

let logData = [];

// Python 스크립트 실행
const options = {
  stdio: ['ignore', 'pipe', 'pipe'], // Redirect stderr to a pipe
  maxBuffer: 1024 * 1024 * 10 // Increase buffer size to 10MB
};

const pythonProcess = spawn('python3', ['../logdata.py'], options);

pythonProcess.stdout.on('data', (data) => {
  console.log(`Python script output: ${data}`);
});

pythonProcess.stderr.on('data', (data) => {
  console.error(`Python script error: ${data}`);
});

pythonProcess.on('close', (code) => {
  console.log(`Python script exited with code ${code}`);
});

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
app.get('/api/data/:cellNumber', (req, res) => {
  const cellNumber = req.params.cellNumber;
  const data = logData.filter(entry => entry.group === cellNumber);
  res.json(data);
});

server.listen(port, '0.0.0.0', () => {
  console.log(`서버가 http://0.0.0.0:${port} 에서 실행 중입니다.`);
});

