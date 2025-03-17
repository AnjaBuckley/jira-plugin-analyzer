# Jira Plugin Release Notes Analyzer

A Streamlit application that analyzes Jira plugin release notes. This repository contains two versions:

## Versions Available

### 1. ChatGPT Version (Main Branch)
- Uses OpenAI's GPT models for analysis
- Requires an OpenAI API key
- More detailed analysis capabilities
- Available in the `main` branch

### 2. Local Version (Ollama Branch)
- Uses local language models via Ollama
- Runs completely offline
- No API keys required
- Available in the `feature/ollama-integration` branch

## Features

- 🔍 Analyze plugin release notes from URLs or PDF files
- 📊 Structured analysis of user changes, admin changes, and compatibility warnings
- 📱 Modern, responsive UI with clear categorization
- 📤 Export results in PDF or Markdown format
- 🔄 Support for multiple release notes sources
- 🎯 Focus on important changes and compatibility issues

## Prerequisites

### For ChatGPT Version (Main Branch)
1. Python 3.8 or higher
2. OpenAI API key
3. Internet connection

### For Local Version (Ollama Branch)
1. Python 3.8 or higher
2. Ollama installed on your system
3. At least one of the following models pulled in Ollama:
   - mistral (recommended)
   - llama3.2
   - codellama

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jira-plugin-analyzer.git
cd jira-plugin-analyzer
```

2. Choose your version:
```bash
# For ChatGPT version (default)
git checkout main

# For Local version with Ollama
git checkout feature/ollama-integration
```

3. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. For Local version (Ollama Branch), install Ollama:
   - Visit [Ollama's website](https://ollama.ai) to download and install
   - Pull the desired model(s):
```bash
ollama pull mistral  # Recommended for best performance
ollama pull llama3.2   # Alternative option
ollama pull codellama  # For technical analysis
```

6. For ChatGPT version (Main Branch), set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
```bash
OPENAI_API_KEY=your_key_here
```

## Usage

1. Start the Streamlit app:
```bash
# For ChatGPT version
streamlit run app.py

# For Local version
streamlit run app_ollama.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. In the app:
   - Enter your current and target Jira versions
   - Provide plugin details
   - Add release notes URLs or upload a PDF file
   - Select your preferred model in the sidebar
   - Click "Analyze Release Notes"

4. View the results and export them in your preferred format

## Model Selection

### ChatGPT Version (Main Branch)
- GPT-3.5-turbo (cost-effective)
- GPT-4-turbo-preview (premium analysis)

### Local Version (Ollama Branch)
- Mistral (recommended for optimal performance)
- Llama3.2 (alternative option)
- CodeLlama (for technical analysis)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 