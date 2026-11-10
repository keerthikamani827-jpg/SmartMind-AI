# SmartMate AI – Smart Chat Assistant

## About the Project
SmartMate AI is an AI-powered chat assistant developed using Python and Streamlit. It allows users to interact with an AI model and receive responses through a simple and user-friendly interface.

The application uses the Qwen 2.5 3B model through Ollama to generate AI responses. SQLite is used to store chat history and messages.

## Features
- AI-powered chat assistant
- New chat creation
- Previous chat history
- Delete chat option
- SQLite database integration
- Ollama local AI model integration
- Simple and professional Streamlit interface

## Technologies Used
- Python
- Streamlit
- Ollama
- Qwen 2.5 3B
- SQLite
- Requests

## Project Structure

```text
SmartMate-AI/
│
├── app.py
├── requirements.txt
└── smartmind.db   (created automatically)
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the Project Folder

```bash
cd SmartMate-AI
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Download Ollama from:

https://ollama.com/

### 5. Download the AI Model

```bash
ollama pull qwen2.5:3b
```

### 6. Run the Application

```bash
streamlit run app.py
```

## Database
SmartMate AI uses SQLite to store:
- Chat details
- User messages
- AI responses

The database file `smartmind.db` is created automatically when the application runs.

## How It Works
1. Open the SmartMate AI application.
2. Create a new chat.
3. Enter a question or message.
4. SmartMate AI sends the message to the Ollama model.
5. The AI generates a response.
6. Chat history is stored in the SQLite database.

## Future Enhancements
- User login and authentication
- Voice input and output
- Multiple AI model support
- Export chat conversations
- Improved response generation

## Conclusion
SmartMate AI provides a simple platform for interacting with a locally running AI model. It combines Python, Streamlit, Ollama, and SQLite to create an interactive AI chat assistant.
