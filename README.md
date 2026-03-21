# Sales Parser 🛒
A robust and automated web scraping and processing pipeline designed to extract, analyze, and serve promotional data from retail stores (e.g., Biedronka).

This project leverages **Selenium** for scraping dynamic web content, **OpenAI (via Instructor)** for intelligent data extraction, **PostgreSQL** for data storage, and **FastAPI** to serve the parsed data. It uses **uv** for blazing-fast dependency management.

## 🚀 Features
* **Automated Scraping:** Uses Selenium to navigate and extract raw data/images from store websites.
* **AI-Powered Parsing:** Integrates OpenAI's LLMs with the `instructor` library and `pydantic` to convert unstructured HTML/text into strictly typed, structured data.
* **Database Integration:** Saves parsed promotional data into a PostgreSQL database.
* **REST API:** Provides endpoints via FastAPI to access the parsed sales data.
* **Modern Stack:** Written in Python 3.13+ with ultra-fast environment management using `uv`.

## 🛠️ Tech Stack
* **Language:** Python >= 3.13
* **Package Manager:** uv
* **Web Scraping:** Playwright (Async)
* **AI & Data Validation:** OpenAI API, Instructor, Pydantic
* **Database:** PostgreSQL (psycopg2)
* **API Framework:** FastAPI

## ⚙️ Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/merdone/sales-parser
   cd sales-parser
    ```
    
2. **Install dependencies:**
Make sure you have `uv` installed. Then, sync the environment (this will automatically download Python 3.13 if needed, create a `.venv`, and install all packages from `uv.lock`):
   ```bash
   uv sync
   ```

3. **Install Playwright Browsers:**
Since the project uses Playwright, you need to install the necessary browser binaries:
    ```bash
    uv run playwright install
    ```

4. **Set up Environment Variables:**
Create a `.env` file in the root directory and add your credentials (do not commit this file to Git!):
    ```env
    # Database Configuration
    DB_HOST=localhost
    DB_PORT=5432
    DB_USER=your_user
    DB_PASSWORD=your_password
    DB_NAME=your_db_name
    
    # OpenAI API Key
    OPENAI_API_KEY=sk-your-secret-api-key
    ```

## 💻 Usage

### Running the Parser

To execute the scraping pipeline (e.g., to fetch the latest Biedronka promotions and save them to the database):

```bash
uv run main.py
```

### Starting the API Server

To start the FastAPI server and access the data via REST endpoints:

```bash
uv run fastapi dev app/server.py
```
The API will be available at `http://localhost:8000`

### Running the React Frontend

To start the modern React frontend:

```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:5173`

For production build:
```bash
npm run build
npm run preview
```

## 📂 Project Structure
* `app/parsers/` - Asynchronous scraping logic for specific stores (e.g., `biedronka_parser.py`).
* `app/pipelines/` - Async orchestration of scraping, AI processing, and database saving.
* `app/services/` - Utility functions and image processing logic.
* `app/database.py` - Database connection and configuration.
* `app/gpt.py` - AI integration using Instructor and OpenAI.
* `app/server.py` - FastAPI application configuration and routes.
* `main.py` - CLI entry point for running the parsers.
* `frontend/` - Modern React + Vite frontend application
  * `src/components/` - Reusable React components
  * `src/hooks/` - Custom React hooks for cart and products management

## 🎨 Frontend / UI

> 🤖 **Note on Frontend Development:**  The core focus and complexity of this project lie in the backend data pipeline — the asynchronous scraping algorithms, LLM-based data extraction, and database architecture. To provide a clean, interactive way to visualize the parsed promotions without shifting focus away from the backend, the React application was generated using AI tools. 

The generated modern React frontend includes:
- ✅ Responsive product grid with lazy loading
- ✅ Category filtering with dropdown menu
- ✅ Product sorting by price and name
- ✅ Shopping cart with localStorage persistence
- ✅ Beautiful, modern UI with CSS styling
- ✅ Hot module reloading for development
- ✅ Optimized production build with Vite

See [frontend/README.md](frontend/README.md) for detailed UI documentation.
