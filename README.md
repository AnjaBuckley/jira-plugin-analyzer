# Jira Plugin Release Notes Analyzer

A streamlined tool for analyzing Jira Data Center plugin release notes. This application helps administrators and users understand important changes, compatibility issues, and security updates when upgrading plugins.

## Features

- 🔍 Intelligent analysis of release notes using AI
  - Automatic categorization of changes
  - Importance level detection
  - Compatibility warning identification
- 📊 Structured output in three categories:
  - User-facing changes
  - Administrative changes
  - Compatibility warnings
- 🎯 Smart importance highlighting
  - Major changes marked with 🔴
  - Minor changes marked with 🟡
  - Compatibility warnings with ⚠️
- 📥 Multiple input methods:
  - Direct URL input (up to 3 URLs)
  - PDF file upload
- 💾 Export options:
  - Markdown format for documentation
  - PDF format for reporting
- 🎨 Clean, modern UI with Streamlit
- 💰 Cost optimization:
  - Choice between GPT-3.5 (cost-effective) and GPT-4 (premium)
  - Token usage tracking
  - Estimated cost display

## Prerequisites

- Python 3.13+
- Virtual environment (recommended)
- OpenAI API key
- macOS, Linux, or Windows

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jira-plugin-analyzer.git
cd jira-plugin-analyzer
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv .venv
source .venv/bin/activate

# On Windows
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```bash
# Create the file
touch .env  # On macOS/Linux
# OR
type nul > .env  # On Windows

# Add your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

5. (Optional) For better performance, install Watchdog:
```bash
# On macOS
xcode-select --install
pip install watchdog

# On other platforms
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

3. Configure your analysis:
   - Select AI model (GPT-3.5 or GPT-4)
   - Enter Jira versions (current and target)
   - Input plugin details
   - Provide release notes via URL or PDF

4. Click "Analyze Release Notes" to get your structured analysis

5. Export results:
   - Use "Export Markdown" for documentation
   - Use "Export PDF" for reports

## Output Format

The analysis is presented in three columns:
1. **User Changes**: Features and improvements affecting end users
2. **Admin Changes**: Configuration, setup, and maintenance updates
3. **Compatibility Warnings**: Version compatibility issues and requirements

Each change is marked with an importance indicator:
- 🔴 Major/Critical changes
- 🟡 Minor changes
- ⚠️ Compatibility warnings

## Cost Optimization

- Default model: GPT-3.5-turbo (cost-effective)
- Optional: GPT-4-turbo for more detailed analysis
- Token usage tracking in the sidebar
- Estimated cost display per analysis

## Security

- Never commit your `.env` file
- Keep your OpenAI API key secure
- Use environment variables for sensitive data
- `.gitignore` configured for security

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
- Powered by OpenAI's GPT models
- Inspired by the needs of Jira administrators

## Support

For issues and feature requests, please use the GitHub issue tracker. 