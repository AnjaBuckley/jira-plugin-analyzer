# Jira Plugin Release Notes Analyzer

A streamlined tool for analyzing Jira Data Center plugin release notes. This application helps administrators and users understand important changes, compatibility issues, and security updates when upgrading plugins.

## Features

- 🔍 Intelligent analysis of release notes using GPT-4
- 📊 Structured output categorizing changes by type:
  - User-facing changes
  - Administrative changes
  - Compatibility warnings
- 🎯 Importance highlighting for critical updates
- 📥 Multiple input methods:
  - Direct URL input (up to 3 URLs)
  - PDF file upload
- 🎨 Clean, modern UI with Streamlit

## Prerequisites

- Python 3.13+
- Virtual environment (recommended)
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jira-plugin-analyzer.git
cd jira-plugin-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```bash
touch .env
```

5. Add your OpenAI API key to the `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

6. (Optional) For better performance, install Watchdog:
```bash
xcode-select --install  # On macOS
pip install watchdog
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to:
- Local: http://localhost:8501
- Network: http://[your-ip]:8501

3. Enter the required information:
   - Current Jira Data Center version
   - Target Jira Data Center version
   - Plugin name
   - Plugin versions (current and target)

4. Input release notes either by:
   - Pasting up to 3 URLs
   - Uploading a PDF file

5. Click "Analyze Release Notes" to get a structured analysis

## Output Format

The analysis is presented in three columns:
1. **User Changes**: Features and improvements affecting end users
2. **Admin Changes**: Configuration, setup, and maintenance updates
3. **Compatibility Warnings**: Version compatibility issues and requirements

Each change is marked with an importance badge:
- 🔴 Major/Critical changes
- 🟡 Minor changes

## Security

- Never commit your `.env` file
- Keep your OpenAI API key secure
- Use environment variables for sensitive data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Streamlit
- Powered by OpenAI's GPT-4
- Inspired by the needs of Jira administrators

## Support

For issues and feature requests, please use the GitHub issue tracker. 