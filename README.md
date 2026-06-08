# ScamShield AI

A comprehensive scam detection system using machine learning and optical character recognition (OCR). Protect yourself from SMS scams, phishing, and fraud with our AI-powered detection system available on web and as a browser extension.

## 🌟 Features

- **ML-based Scam Detection**: Trained BERT model for text classification
- **OCR Support**: Extract and analyze text from images
- **Real-time Feedback**: Retrain models with user feedback
- **Web Interface**: React-based frontend for easy interaction
- **REST API**: FastAPI backend for integration
- **Browser Extension**: Chrome extension for real-time scam detection
- **Multi-modal Analysis**: SMS, email, and image-based scam detection

## 📁 Project Structure

```
ScamShield/
├── backend/              # FastAPI application
│   ├── main.py          # Main application entry point
│   ├── routes/          # API routes
│   ├── services/        # ML models and utilities
│   └── requirements.txt  # Python dependencies
├── frontend/            # React + Vite application
│   ├── src/            # React components
│   ├── dist/           # Built frontend (production)
│   └── package.json    # Node dependencies
├── extension/          # Chrome browser extension
│   ├── manifest.json   # Extension configuration
│   ├── popup.html      # Extension popup UI
│   ├── popup.js        # Extension popup logic
│   ├── content.js      # Content script for page analysis
│   └── icons/          # Extension icons
├── datasets/           # Training datasets
│   └── sms_spam/       # SMS spam dataset
└── Dockerfile          # Docker container setup
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- Tesseract OCR
- Chrome/Chromium browser (for extension)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
npm run build
```

### Run Backend Locally

```bash
cd backend
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

### Run Frontend Locally

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 🔌 Browser Extension Installation

### Local Development

1. Navigate to `chrome://extensions/`
2. Enable **"Developer mode"** (toggle in top right)
3. Click **"Load unpacked"**
4. Select the `extension/` folder from the project

### Using the Extension

- Click the ScamShield icon in your Chrome toolbar
- The extension will:
  - Scan SMS messages and emails on the page
  - Highlight potential scams
  - Provide real-time detection results
  - Allow you to report false positives

### Publishing to Chrome Web Store

To publish the extension:

1. Create a [Chrome Developer account](https://chrome.google.com/webstore/developer/dashboard)
2. Pay the $5 one-time developer fee
3. Create a ZIP file of the `extension/` folder
4. Upload to Chrome Web Store with:
   - Extension name
   - Description
   - Category (Productivity/Safety)
   - Screenshots and icons (128x128)
5. Submit for review (typically 24-48 hours)

## 🌐 Deployment

### Frontend - Vercel

```bash
# Already built in dist/ folder
# Deploy via Vercel dashboard or CLI

vercel
```

**Live**: https://scamshield-xyz.vercel.app

**Environment Variables:**
```
VITE_API_URL=https://web-production-75af9.up.railway.app
```

### Backend - Railway

```bash
# Deployed via Docker
# Connect GitHub repository to Railway
# Auto-deploys on git push
```

**Live**: https://web-production-75af9.up.railway.app

**Environment Variables:**
```
PORT=8000
PYTHONUNBUFFERED=1
```

## 📡 API Endpoints

### Health Check
- `GET /` - Server status

### Scam Detection
- `POST /api/scan` - Scan text for scam
  - Request: `{"text": "message content"}`
  - Response: `{"is_scam": true/false, "confidence": 0.95}`

- `POST /api/scan-image` - Scan image for scam
  - Request: FormData with image file
  - Response: `{"text": "extracted text", "is_scam": true/false}`

### Feedback & Retraining
- `POST /api/feedback` - Submit feedback for model improvement
  - Request: `{"text": "message", "label": "spam/ham", "feedback": "reason"}`

- `POST /api/retrain` - Retrain model with accumulated feedback
  - Response: `{"status": "retraining", "message": "Model update initiated"}`

## 🔧 Environment Variables

Create a `.env` file in the backend directory:

```env
DEBUG=False
MODEL_PATH=./services/bert_scam_model
PORT=8000
PYTHONUNBUFFERED=1
```

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
docker-compose up --build
```

### Dockerfile Features
- Python 3.11-slim base image
- Tesseract OCR and OpenCV support
- Frontend built into container
- FastAPI backend with Uvicorn

## 📊 Model Information

- **Architecture**: BERT (Bidirectional Encoder Representations from Transformers)
- **Training Data**: SMS Spam Dataset (5,000+ messages)
- **Accuracy**: ~95% on test set
- **Retraining**: Supports continuous learning from user feedback

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
pytest
```

### Test Scam Detection API

```bash
curl -X POST "http://localhost:8000/api/scan" \
  -H "Content-Type: application/json" \
  -d '{"text": "Congratulations! You won $1,000,000! Click here to claim."}'
```

## 📱 Supported Platforms

- **Web**: Desktop and mobile browsers
- **Chrome Extension**: Chrome, Edge, Brave browsers
- **API**: Any platform via REST API

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- BERT Model from Hugging Face Transformers
- Tesseract OCR for text extraction
- FastAPI for backend framework
- React + Vite for frontend framework
- Railway for backend deployment
- Vercel for frontend deployment

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: shreyabbgn@gmail.com
- Check the [Discussions](https://github.com/shreyabbgn-source/ScamShield/discussions) section

## 🔐 Security Notice

ScamShield is designed to help detect potential scams, but it's not foolproof. Always:
- Verify sender identity independently
- Never click suspicious links
- Be cautious with personal information
- Report actual scams to authorities

---

**Last Updated**: June 2026  
**Version**: 1.0.0
