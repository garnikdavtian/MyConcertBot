# 🎶 Concert Knowledge Assistant

This project provides a Streamlit-based AI assistant designed to answer questions about concerts, tours, venues, and performers. It leverages local document ingestion into a FAISS vector store and uses Ollama for large language model (LLM) interactions. When local information is insufficient, it can fall back to online searches via SerpAPI.

## ✨ Features

-   **Document Ingestion:** Upload or paste text documents related to concerts. The system summarizes content and stores it in a local FAISS vector database.
-   **Concert-Related Filtering:** Automatically checks if ingested or queried text is relevant to concerts before processing.
-   **Chat Assistant:** Ask questions about ingested documents.
-   **Online Fallback:** If a question cannot be answered from the local knowledge base, the system performs an online search (via SerpAPI) and provides relevant snippets.
-   **Local LLM Support:** Uses Ollama for all language model operations, allowing for offline use once models are downloaded.

## 🚀 Getting Started

Follow these steps to set up and run the Concert Knowledge Assistant.

### 📋 Prerequisites

Before you begin, ensure you have the following installed:

-   **Python 3.9+:**
    ```bash
    python --version
    ```
-   **Ollama:** Download and install Ollama from [ollama.com](https://ollama.com/).
    -   After installation, pull the required models:
        ```bash
        ollama pull llama3
        ollama pull nomic-embed-text
        ```
-   **SerpAPI Key (Optional but Recommended):** For online search fallback, you'll need an API key from [serpapi.com](https://serpapi.com/). Set it as an environment variable `SERPAPI_KEY`.

### 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/concert-assistant.git](https://github.com/your-username/concert-assistant.git)
    cd concert-assistant
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    -   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Create a `.env` file:**
    If you plan to use the online search functionality, create a file named `.env` in the root directory of the project and add your SerpAPI key:
    ```
    SERPAPI_KEY="YOUR_SERPAPI_KEY_HERE"
    ```
    Replace `YOUR_SERPAPI_KEY_HERE` with your actual SerpAPI key.

### ▶️ Running the Application

1.  **Ensure Ollama is running:** The `main.py` script will attempt to start the Ollama daemon if it's not already running. You can also manually start it:
    ```bash
    ollama serve
    ```

2.  **Run the Streamlit application:**
    ```bash
    streamlit run main.py
    ```

    Your web browser should automatically open to the Streamlit interface (usually `http://localhost:8501`).

## 📁 Project Structure

-   `main.py`: The main Streamlit application logic.
-   `filter_docs.py`: Handles document ingestion and checking for concert relevance.
-   `llm_utils.py`: Utility functions for LLM interactions (summarization, relevance check).
-   `qa_system.py`: Manages the question-answering logic, including FAISS retrieval and online fallback.
-   `online_lookup.py`: Functions for performing online searches via SerpAPI.
-   `requirements.txt`: Lists all Python dependencies.
-   `.gitignore`: Specifies files and directories to be ignored by Git.
-   `faiss_db/`: (Created automatically) Directory where the FAISS vector store is saved.
-   `documents/`: (Created automatically) Directory where ingested text files are stored.

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.