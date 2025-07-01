# Kokoro TTS Web Application Setup Instructions

## Overview

This is a complete web application that provides a modern interface for the Kokoro TTS (Text-to-Speech) model. The application consists of:

- **Backend**: FastAPI server that wraps the Kokoro TTS model
- **Frontend**: Next.js React application with TypeScript and Tailwind CSS

## Prerequisites

### Required Software

- Python 3.8+ with pip
- Node.js 18+ with npm
- Git (for cloning repositories)

### Python Dependencies

The backend requires the Kokoro TTS model and related dependencies:

```bash
pip install kokoro>=0.9.4
```

## Project Structure

```
Kokoro-TTS/
├── api-server/          # FastAPI backend
│   ├── main.py         # Main FastAPI application
│   ├── models.py       # Pydantic models
│   ├── tts_service.py  # Kokoro TTS integration
│   ├── run.py          # Server startup script
│   └── requirements.txt
├── web-app/            # Next.js frontend
│   ├── src/
│   │   ├── app/        # Next.js app router
│   │   ├── components/ # React components
│   │   └── lib/        # API client and utilities
│   ├── package.json
│   └── .env.local      # Environment configuration
├── app.py              # Original Kokoro Gradio app
├── plan.md             # Development plan
└── setup-instructions.md
```

## Setup Instructions

### Step 1: Backend Setup

1. **Navigate to the API server directory:**

   ```bash
   cd api-server
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server:**

   ```bash
   python run.py
   ```

   The API server will start on `http://localhost:8000`

   - API documentation: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/api/health`

### Step 2: Frontend Setup

1. **Open a new terminal and navigate to the web app directory:**

   ```bash
   cd web-app
   ```

2. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm run dev
   ```

   The web application will be available at `http://localhost:3000`

## Usage

### Web Interface Features

1. **Text Input**

   - Enter text up to 5,000 characters
   - Use sample text buttons for quick testing
   - Character counter with visual feedback

2. **Voice Selection**

   - Choose from multiple English voices (American and British)
   - Male and female options available
   - Voice information display

3. **Speech Controls**

   - Adjustable speed (0.5x to 2.0x)
   - GPU acceleration toggle
   - Real-time parameter adjustment

4. **Audio Output**

   - Integrated audio player with controls
   - Download generated audio files
   - Volume control and seeking

5. **Additional Features**
   - Phonetic token display
   - Error handling and user feedback
   - Responsive design for mobile and desktop

### API Endpoints

The backend provides several REST API endpoints:

- `GET /api/voices` - List available voices
- `POST /api/tts` - Generate speech from text
- `GET /api/health` - Health check
- `DELETE /api/audio/{filename}` - Delete audio files

### Example API Usage

```bash
# Get available voices
curl http://localhost:8000/api/voices

# Generate speech
curl -X POST http://localhost:8000/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of Kokoro TTS!",
    "voice": "af_heart",
    "speed": 1.0,
    "use_gpu": true
  }'
```

## Configuration

### Environment Variables

**Frontend (.env.local):**

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend:**

- No additional configuration required for local development
- GPU acceleration automatically detected

### Customization Options

1. **Adding New Voices:**

   - Edit `CHOICES` dictionary in `api-server/tts_service.py`
   - Restart the backend server

2. **Styling Modifications:**

   - Modify Tailwind classes in React components
   - Update `web-app/src/app/globals.css` for global styles

3. **API Configuration:**
   - Change ports in `api-server/run.py` and frontend environment

## Troubleshooting

### Common Issues

1. **"Failed to load voices" error:**

   - Ensure the backend server is running on port 8000
   - Check that Kokoro dependencies are properly installed

2. **CORS errors:**

   - Verify the frontend is running on port 3000
   - Check CORS configuration in `api-server/main.py`

3. **Audio generation fails:**

   - Check that the Kokoro model is properly installed
   - Verify GPU/CUDA setup if using GPU acceleration

4. **Module import errors:**
   - Ensure all dependencies are installed
   - Check Python path configuration

### Performance Tips

1. **GPU Acceleration:**

   - Enable GPU mode for faster generation
   - Fallback to CPU if GPU fails

2. **Text Optimization:**

   - Use proper punctuation for better prosody
   - Keep text under 5,000 characters for best performance

3. **Browser Compatibility:**
   - Use modern browsers for full feature support
   - Enable JavaScript for full functionality

## Development

### Running in Development Mode

Both servers support hot reloading:

- **Backend**: `uvicorn main:app --reload`
- **Frontend**: `npm run dev`

### Building for Production

**Frontend:**

```bash
cd web-app
npm run build
npm start
```

**Backend:**

```bash
cd api-server
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Support

For issues related to:

- **Kokoro TTS Model**: Check the [official repository](https://huggingface.co/hexgrad/Kokoro-82M)
- **Web Application**: Review the component code in `web-app/src/components/`
- **API Integration**: Check the FastAPI documentation at `http://localhost:8000/docs`

## License

This project integrates with the Kokoro TTS model. Please refer to the original model's license terms for usage restrictions.
