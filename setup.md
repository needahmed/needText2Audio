# Kokoro-TTS Project Setup Guide

This guide provides step-by-step instructions to set up and run the Kokoro-TTS project, which includes a Python FastAPI backend and a Next.js frontend.

## Prerequisites

- [Python](https://www.python.org/downloads/) (version 3.8 or higher)
- [Node.js](https://nodejs.org/en/download/) (version 18 or higher)
- `pip` (Python package installer)
- `npm` (Node package manager)

## Setup Instructions

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

First, clone the project repository to your local machine.

```bash
git clone <repository-url>
cd Kokoro-TTS
```

### 2. Backend Setup (API Server)

The backend is a FastAPI server that handles the text-to-speech processing.

**Navigate to the API server directory:**

```bash
cd api-server
```

**Create a virtual environment (recommended):**

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Install the required Python packages:**

We will use `requirements-simple.txt` for a straightforward local development setup.

```bash
pip install -r requirements-simple.txt
```

**Run the API server:**

```bash
python simple_run.py
```

The server will start, download the necessary TTS models on the first run, and become available at `http://localhost:8000`. You can keep this terminal window open.

### 3. Frontend Setup (Web App)

The frontend is a Next.js application that provides the user interface.

**Open a new terminal window** and navigate to the web app directory:

```bash
cd web-app
```

**Install the required Node.js packages:**

```bash
npm install
```

**Run the development server:**

```bash
npm run dev
```

The frontend application will start and become available at `http://localhost:3000`.

### 4. Access the Application

Once both the backend and frontend are running, you can open your web browser and navigate to:

**[http://localhost:3000](http://localhost:3000)**

You should now be able to use the Kokoro-TTS application. The frontend will communicate with the backend running on port 8000.
