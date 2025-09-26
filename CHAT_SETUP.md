# Chat Integration Setup

This document explains how to set up the chat functionality with Swisscom's Apertus 70B API.

## Backend Setup

1. Install the required dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Set the environment variable for the Swisscom API key:

```bash
export SWISS_AI_PLATFORM_API_KEY=mJ9UlAavIK70WEBR7JfcyXhQuU8U
```

Or create a `.env` file in the backend directory:

```
SWISS_AI_PLATFORM_API_KEY=mJ9UlAavIK70WEBR7JfcyXhQuU8U
```

3. Start the backend server:

```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Set the API base URL (optional, defaults to http://localhost:8000):

```bash
export NEXT_PUBLIC_API_BASE=http://localhost:8000
```

3. Start the frontend development server:

```bash
cd frontend
npm run dev
```

## Features

- **Real-time Chat**: Chat with the Apertus 70B model through Swisscom's API
- **Chat History**: Maintains conversation context across messages
- **Financial Focus**: The AI is configured as a financial analyst
- **Auto-scroll**: Chat automatically scrolls to show new messages
- **Loading States**: Visual feedback during API calls
- **Error Handling**: Graceful error handling with user feedback

## API Endpoints

- `POST /chat` - Send a message and get a response from the AI
- `GET /portfolio` - Get portfolio data
- `GET /investment-strategy` - Get investment strategy data
- `GET /healthz` - Health check endpoint

## Usage

1. Open the application in your browser (http://localhost:3000)
2. Use the chat panel on the right side to interact with the AI
3. The AI is configured to provide financial analysis and investment advice
4. Chat history is maintained throughout the session
