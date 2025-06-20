# BanBan 教育 AI 視頻生成器 (BanBan Education AI Video Generator)

這是一個基於 AI 的教育媒體生成系統，專為 BanBan 教育平台設計。本系統能夠根據教育內容自動生成高品質的教學視頻，幫助教師豐富教學素材。

## 主要功能

- **自動生成教學動畫**：使用 Manim 庫根據文本內容自動生成數學和科學教學動畫
- **AI 語音合成**：使用 Edge TTS 將文本轉換為自然流暢的語音配音
- **多語言支持**：支持多種語言的文本和語音處理
- **RESTful API**：提供便捷的 API 接口，方便與其他系統集成
- **視頻存儲與管理**：所有生成的視頻都存儲在 Google Cloud Storage，便於訪問和管理

## 技術棧

- **後端框架**：FastAPI
- **數據庫**：MongoDB
- **AI 模型**：Google Gemini AI
- **視頻生成**：Manim
- **語音合成**：Edge TTS
- **雲存儲**：Google Cloud Storage
- **容器化**：Docker

## 安裝指南

### 前置需求

- Python 3.12+
- Poetry (依賴管理)
- FFmpeg (視頻處理)
- MongoDB
- Google Cloud 帳戶和憑證

### 安裝步驟

1. 克隆儲存庫：

```bash
git clone https://github.com/yourorganization/banban_EduAI_VideoGen.git
cd banban_EduAI_VideoGen
```

2. 使用 Poetry 安裝依賴：

```bash
poetry install
```

3. 設置環境變量：

創建 `.env` 文件：

```
APP_NAME=banban-eduai-videogen
APP_ENV=dev
APP_VERSION=0.1.0
MONGODB_URI=your_mongodb_uri
MONGODB_DATABASE=MediaStorage
GOOGLE_SA_CREDENTIALS_PATH=./app/core/credentials/google.json
```

4. 確保 Google 憑證文件位於正確位置：

```
app/core/credentials/google.json
```

## 使用方法

### 啟動服務

```bash
poetry run python -m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

或使用 Docker：

```bash
docker build -t banban-eduai-videogen .
docker run -p 8000:8000 banban-eduai-videogen
```

### API 文檔

啟動服務後，訪問以下 URL 查看 API 文檔：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端點

### 視頻生成

```
POST /video/generate/{client_id}
```

請求體：

```json
{
  "text": "需要講解的教育內容",
  "voice": "zh-TW-HsiaoChenNeural",
  "image_base64": "可選的圖片 base64 編碼"
}
```

響應：

```json
{
  "data": {
    "client_id": "client123",
    "task_id": "video_client123_1621234567",
    "status": "processing",
    "metadata": {
      "text": "需要講解的教育內容",
      "image_base64": true
    },
    "gcs_public_url": "https://storage.googleapis.com/generate_educational_video/mentor/client123/video_client123_1621234567.mp4",
    "created_at": "2023-05-17T12:34:56.789Z"
  }
}
```

### 查詢視頻任務列表

```
GET /video/tasks/{client_id}
```

### 查詢單個視頻任務

```
GET /video/tasks/{client_id}/{task_id}
```

### 刪除視頻任務

```
DELETE /video/tasks/{client_id}/{task_id}
```

### 刪除所有視頻任務

```
DELETE /video/tasks/{client_id}
```

## 部署

本專案支持使用 Google Cloud Build 進行 CI/CD 部署：

```
gcloud builds submit --config cloudbuild.yaml .
```

## 許可證

查看 [LICENSE](LICENSE) 文件了解詳情。

## 貢獻指南

1. Fork 本儲存庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request