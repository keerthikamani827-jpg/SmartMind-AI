import sqlite3
import uuid
from pathlib import Path

import requests
import streamlit as st

# --------------------------------------------------
# SmartMate AI - Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="SmartMate AI",
    page_icon="💬",
    layout="wide"
)

APP_TITLE = "SmartMate AI"
MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434"
DB = Path(__file__).with_name("smartmind.db")


# --------------------------------------------------
# Database Functions
# --------------------------------------------------
def connect():
    return sqlite3.connect(DB)


def setup_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES chats(id)
            )
        """)


def new_chat():
    chat_id = str(uuid.uuid4())
    with connect() as con:
        con.execute(
            "INSERT INTO chats (id, title) VALUES (?, ?)",
            (chat_id, "New chat")
        )
    return chat_id


def get_chats():
    with connect() as con:
        return con.execute(
            "SELECT id, title FROM chats ORDER BY rowid DESC"
        ).fetchall()


def get_messages(chat_id):
    with connect() as con:
        rows = con.execute(
            """
            SELECT role, content
            FROM messages
            WHERE chat_id = ?
            ORDER BY id
            """,
            (chat_id,)
        ).fetchall()
    return [{"role": role, "content": content} for role, content in rows]


def save_message(chat_id, role, content):
    with connect() as con:
        con.execute(
            """
            INSERT INTO messages (chat_id, role, content)
            VALUES (?, ?, ?)
            """,
            (chat_id, role, content)
        )


def update_chat_title(chat_id, first_message):
    title = " ".join(first_message.strip().split())
    if title:
        with connect() as con:
            con.execute(
                "UPDATE chats SET title = ? WHERE id = ? AND title = ?",
                (title[:35], chat_id, "New chat")
            )


def delete_chat(chat_id):
    with connect() as con:
        con.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        con.execute("DELETE FROM chats WHERE id = ?", (chat_id,))


# --------------------------------------------------
# Ollama Functions
# --------------------------------------------------
def ollama_ready():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return response.ok
    except requests.RequestException:
        return False


def ask_ai(messages):
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False
        },
        timeout=180
    )
    response.raise_for_status()
    result = response.json()
    return result["message"]["content"]


# --------------------------------------------------
# Application Setup
# --------------------------------------------------
setup_db()

if "chat_id" not in st.session_state:
    st.session_state.chat_id = new_chat()


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.title(APP_TITLE)
    st.caption("Your personal AI chat assistant")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.chat_id = new_chat()
        st.rerun()

    chats = get_chats()
    chat_ids = [chat[0] for chat in chats]
    chat_titles = {chat[0]: chat[1] for chat in chats}

    if st.session_state.chat_id not in chat_ids:
        st.session_state.chat_id = new_chat()
        st.rerun()

    selected_chat = st.selectbox(
        "Previous Chats",
        options=chat_ids,
        index=chat_ids.index(st.session_state.chat_id),
        format_func=lambda chat_id: chat_titles.get(chat_id, "New chat")
    )

    if selected_chat != st.session_state.chat_id:
        st.session_state.chat_id = selected_chat
        st.rerun()

    if st.button("Delete Current Chat", use_container_width=True):
        delete_chat(st.session_state.chat_id)
        st.session_state.chat_id = new_chat()
        st.rerun()

    st.divider()
    st.caption(f"Model: {MODEL}")
    st.caption("Database: SQLite")


# --------------------------------------------------
# Main Page
# --------------------------------------------------
st.title("SmartMate AI Assistant")
st.write(
    "Ask questions, explore ideas, learn new concepts, "
    "or get help with programming."
)

if ollama_ready():
    st.success("Ollama is connected.")
else:
    st.error(
        "Ollama is not running. Open Ollama and make sure it is running "
        "before sending a message."
    )

st.divider()

current_chat_id = st.session_state.chat_id
messages = get_messages(current_chat_id)

if not messages:
    st.subheader("Start a conversation")
    st.write("Type a message below to begin chatting with SmartMate AI.")

# Display saved conversation.
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# Chat Input and AI Response
# --------------------------------------------------
prompt = st.chat_input("Type your message...")

if prompt:
    chat_id = st.session_state.chat_id

    save_message(chat_id, "user", prompt)
    update_chat_title(chat_id, prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            conversation_history = get_messages(chat_id)[-12:]
            ai_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are SmartMate, a helpful AI assistant. "
                        "Give clear, accurate, and simple answers. "
                        "Use examples when they help explain a concept."
                    )
                },
                *conversation_history
            ]

            with st.spinner("SmartMate is thinking..."):
                answer = ask_ai(ai_messages)

            st.markdown(answer)
            save_message(chat_id, "assistant", answer)

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to Ollama. Please check that Ollama "
                "is running at http://localhost:11434."
            )
        except requests.exceptions.Timeout:
            st.error("The AI response took too long. Please try again.")
        except requests.exceptions.HTTPError as error:
            st.error(
                f"Ollama returned an HTTP error: {error}. "
                f"Check that the model '{MODEL}' is installed."
            )
        except (KeyError, ValueError):
            st.error(
                "Received an unexpected response from Ollama. "
                "Please try again."
            )
        except requests.RequestException as error:
            st.error(f"Request failed: {error}")

    st.rerun()
