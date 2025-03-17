# Jira Plugin Release Notes Analyzer (Local)

A Streamlit application that analyzes Jira plugin release notes using local language models via Ollama. This version runs completely offline and doesn't require any API keys.

## Features

- 🔍 Analyze plugin release notes from URLs or PDF files
- 🤖 Uses local language models (Mistral, Llama2, or CodeLlama) via Ollama
- 📊 Structured analysis of user changes, admin changes, and compatibility warnings
- 📱 Modern, responsive UI with clear categorization
- 📤 Export results in PDF or Markdown format
- 🔄 Support for multiple release notes sources
- 🎯 Focus on important changes and compatibility issues

## Prerequisites

1. Python 3.8 or higher
2. Ollama installed on your system
3. At least one of the following models pulled in Ollama:
   - mistral (recommended)
   - llama2
   - codellama

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jira-plugin-analyzer.git
cd jira-plugin-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Ollama:
   - Visit [Ollama's website](https://ollama.ai) to download and install
   - Pull the desired model(s):
```bash
ollama pull mistral  # Recommended for best performance
ollama pull llama2   # Alternative option
ollama pull codellama  # For technical analysis
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app_ollama.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. In the app:
   - Enter your current and target Jira versions
   - Provide plugin details
   - Add release notes URLs or upload a PDF file
   - Select your preferred Ollama model in the sidebar
   - Click "Analyze Release Notes"

4. View the results and export them in your preferred format

## Model Selection

The app supports three models via Ollama:

- **Mistral** (Recommended)
  - Best overall performance
  - Good balance of speed and accuracy
  - Optimized for general text analysis

- **Llama2**
  - Good for general analysis
  - Slightly slower than Mistral
  - More conservative in its analysis

- **CodeLlama**
  - Specialized for technical content
  - Best for complex technical changes
  - May be slower than other models

## Troubleshooting

1. **Ollama Connection Issues**
   - Ensure Ollama is running on your system
   - Check if the selected model is pulled (`ollama list`)
   - Verify your firewall settings

2. **PDF Processing Issues**
   - Ensure the PDF is not password-protected
   - Check if the PDF contains text (not scanned images)
   - Try converting scanned PDFs to text first

3. **URL Processing Issues**
   - Verify the URLs are accessible
   - Check if the URLs require authentication
   - Ensure the content is HTML (not JavaScript-rendered)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 