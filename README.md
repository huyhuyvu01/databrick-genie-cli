# Databricks Genie CLI

A Command Line Interface for interacting with Databricks Genie spaces.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (Recommended) or Python 3.9+
- Databricks Account with Genie Space access.

## Setup

1. **Clone the repository** (if you haven't already).
2. **Configure Environment Variables**:

   Copy `.env.example` to `.env` and fill in your details. Get your authentication credentials [here](https://databricks-sdk-py.readthedocs.io/en/latest/authentication.html):
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```env
   DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   DATABRICKS_TOKEN=dapi... (PAT tokens)
   GENIE_SPACE_ID=01abcdef12345678
   ```

## Usage

Run the CLI using `uv`:

```bash
uv run main.py
```

Or with standard pip:

```bash
pip install -r requirements.txt
python main.py
```

## Features

- **Rich UI**: Markdown and Table rendering in terminal.
- **Conversational**: Maintains context within a session.
- **Data Visualization**: Displays SQL results in formatted tables.
