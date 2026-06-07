# ScamShield AI

A comprehensive scam detection system using machine learning and optical character recognition (OCR).

## Features

- **ML-based Scam Detection**: Trained BERT model for text classification
- **OCR Support**: Extract and analyze text from images
- **Real-time Feedback**: Retrain models with user feedback
- **Web Interface**: React-based frontend for easy interaction
- **REST API**: FastAPI backend for integration

## Project Structure

```
ScamShield/
├── backend/              # FastAPI application
│   ├── main.py          # Main application entry point
│   ├── routes/          # API routes
│   ├── services/        # ML models and utilities
│   └── requirements.txt  # Python dependencies
├── frontend/            # React application
│   ├── src/            # React components
│   └── package.json    # Node dependencies
├── extension/          # Browser extension
└── datasets/           # Training datasets
```

## Installation

### Prerequisites
- Python 3.11+
- Node.js 16+
- Tesseract OCR

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
npm run dev
```

### Run Backend

```bash
cd backend
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

### Run Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:5173`

## API Endpoints

- `POST /api/scan` - Scan text or image for scam
- `POST /api/feedback` - Submit feedback for model retraining
- `POST /api/retrain` - Retrain model with feedback

## Deployment

### Option 1: Heroku

```bash
heroku login
heroku create scamshield-app
git push heroku main
```

### Option 2: Docker

```bash
docker-compose up --build
```

### Option 3: Railway.app

1. Go to https://railway.app
2. Connect your GitHub repository
3. Deploy automatically

### Option 4: Render.com

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub and deploy

## Environment Variables

Create a `.env` file in the backend directory:

```env
DEBUG=False
MODEL_PATH=./services/bert_scam_model
```

## Development

### Run with Docker

```bash
docker-compose up
```

### Run Tests

```bash
cd backend
pytest
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
