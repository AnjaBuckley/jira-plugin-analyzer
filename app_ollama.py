import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Jira Plugin Release Notes Analyzer (Local)",
    page_icon="🚀",
    layout="wide"
)

import json
from typing import List, Dict, Any
import PyPDF2
import io
import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from fpdf import FPDF
import ollama

# Debug information in expandable section
with st.expander("Debug Information", expanded=False):
    st.write(f"Current working directory: {os.getcwd()}")
    st.write("Checking Ollama connection...")
    try:
        # Test Ollama connection
        response = ollama.list()
        st.success("Ollama connection successful!")
        if 'models' in response:
            st.write("Available models:", [model.get('name', 'Unknown') for model in response['models']])
        else:
            st.write("No models found. Please pull a model using: ollama pull mistral")
    except Exception as e:
        st.error(f"Error connecting to Ollama: {str(e)}")
        st.error("Please ensure Ollama is running and accessible")
        st.stop()

SYSTEM_PROMPT = """You are a Jira plugin release notes analyzer. Your task is to analyze release notes and provide a concise, structured summary of the most important changes between the specified version range.

IMPORTANT: Analyze the actual content of the release notes provided. Do not return a template or placeholder text. Extract real changes from the provided release notes.

VERSION RANGE ANALYSIS:
- Only include changes that are relevant to the specified version range (from current_version to target_version)
- For compatibility information, include ALL relevant compatibility details that affect the version range
- Include breaking changes that affect the version range, even if they were introduced in earlier versions
- Pay special attention to version-specific requirements and dependencies

Focus on these key areas:
1. Major user-facing changes (new features, significant UI changes, important bug fixes)
2. Critical admin/technical changes (security updates, performance improvements, configuration changes)
3. Compatibility information (Jira version compatibility, breaking changes, deprecations)

For each change:
- Extract the version number if specified
- Determine if it's a major or minor change
- Provide a clear, concise description
- Remove any redundant information
- Skip minor bug fixes unless they're significant
- Combine similar changes into single items
- Keep only the most important changes (max 5-7 per category)

Format your response as follows:

New Features:
- [Feature 1] Description of new feature 1 (Version X.Y.Z)
- [Feature 2] Description of new feature 2 (Version A.B.C)

Bugs Fixed:
- [Bug Fix 1] Description of bug fix 1 (Version X.Y.Z)
- [Bug Fix 2] Description of bug fix 2 (Version A.B.C)

Compatibility Issues and Breaking Changes:
- [Breaking Change 1] Explanation of breaking change 1 (Version X.Y.Z)
- [Breaking Change 2] Explanation of breaking change 2 (Version A.B.C)
- [Compatibility Issue 1] Explanation of compatibility issue 1 (Version X.Y.Z)
- [Compatibility Issue 2] Explanation of compatibility issue 2 (Version A.B.C)

Other Noteworthy Changes:
- [Noteworthy Change 1] Description of noteworthy change 1 (Version X.Y.Z)
- [Noteworthy Change 2] Description of noteworthy change 2 (Version A.B.C)

Remember to:
- Only include changes relevant to the specified version range
- Include ALL compatibility information that affects the version range
- Prioritize breaking changes and compatibility issues
- Include specific version numbers when mentioned in the notes
- Highlight any security-related changes
- Note any deprecations or removals
- Pay special attention to version-specific requirements and dependencies
- Include any breaking changes that were introduced in earlier versions but still affect the target version range"""

USER_PROMPT_TEMPLATE = """Analyze these release notes and provide a structured summary:

Current Jira Version: {current_version}
Target Jira Version: {target_version}
Plugin: {plugin_name}

Release Notes:
{release_notes}

Analyze the release notes and provide a summary following exactly the same format as shown in the system prompt example. Focus on the most important changes between the current and target versions, with special attention to compatibility issues and breaking changes."""

def analyze_with_ollama(text: str, plugin_name: str, current_version: str, target_version: str) -> Dict[str, List[Dict[str, Any]]]:
    """Use Ollama to analyze the release notes."""
    try:
        # Prepare the prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            current_version=current_version,
            target_version=target_version,
            plugin_name=plugin_name,
            release_notes=text
        )

        # Get the selected model
        model = st.session_state.get('ollama_model', 'mistral')
        
        # Show which model is being used
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Current Analysis")
        st.sidebar.info(f"🤖 Using model: {model}")
        
        # Debug information
        with st.expander("Debug: Analysis Details", expanded=True):
            st.write("Input text length:", len(text))
            st.write("Model:", model)
            st.write("Current version:", current_version)
            st.write("Target version:", target_version)
        
        # Call Ollama API
        st.info("Calling Ollama API...")
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Debug: Show raw response
        with st.expander("Debug: Raw Response", expanded=True):
            st.write("Response received:", response)

        # Parse the response
        analysis_text = response['message']['content']
        
        # Debug: Show parsed text
        with st.expander("Debug: Parsed Text", expanded=True):
            st.write("Analysis text:", analysis_text)
        
        results = {
            'user': [],
            'admin': [],
            'compatibility': []
        }
        
        # Split into sections
        sections = analysis_text.split('\n\n')
        current_section = None
        
        for section in sections:
            if not section.strip():
                continue
            
            # Check for section headers
            if 'New Features' in section:
                current_section = 'user'
                items = section.replace('New Features:', '').strip().split('\n')
                for item in items:
                    if item.strip().startswith(('*', '-')):
                        content = item.strip('*- ').strip()
                        if content.lower() != 'none specified in the provided release notes.':
                            # Determine importance based on content
                            importance = 'major' if any(keyword in content.lower() for keyword in 
                                ['breaking change', 'deprecation', 'security', 'critical', 'important']) else 'minor'
                            results['user'].append({
                                'importance': importance,
                                'text': content,
                                'version': 'N/A',
                                'category': 'New Features'
                            })
            
            elif 'Bugs Fixed' in section:
                current_section = 'user'
                items = section.replace('Bugs Fixed:', '').strip().split('\n')
                for item in items:
                    if item.strip().startswith(('*', '-')):
                        content = item.strip('*- ').strip()
                        # Determine importance based on content
                        importance = 'major' if any(keyword in content.lower() for keyword in 
                            ['security', 'critical', 'important', 'fix']) else 'minor'
                        results['user'].append({
                            'importance': importance,
                            'text': content,
                            'version': 'N/A',
                            'category': 'Bug Fixes'
                        })
            
            elif 'Breaking Changes' in section:
                current_section = 'admin'
                items = section.replace('Breaking Changes:', '').strip().split('\n')
                for item in items:
                    if item.strip().startswith(('*', '-')):
                        content = item.strip('*- ').strip()
                        results['admin'].append({
                            'importance': 'major',
                            'text': content,
                            'version': 'N/A',
                            'category': 'Breaking Changes'
                        })
            
            elif 'Compatibility Issues' in section:
                current_section = 'compatibility'
                items = section.replace('Compatibility Issues:', '').strip().split('\n')
                for item in items:
                    if item.strip().startswith(('*', '-')):
                        content = item.strip('*- ').strip()
                        results['compatibility'].append({
                            'text': content
                        })
            
            elif 'Other Noteworthy Changes' in section:
                current_section = 'admin'
                items = section.replace('Other Noteworthy Changes:', '').strip().split('\n')
                for item in items:
                    if item.strip().startswith(('*', '-')):
                        content = item.strip('*- ').strip()
                        # Determine importance based on content
                        importance = 'major' if any(keyword in content.lower() for keyword in 
                            ['security', 'critical', 'important', 'update']) else 'minor'
                        results['admin'].append({
                            'importance': importance,
                            'text': content,
                            'version': 'N/A',
                            'category': 'Other Changes'
                        })
        
        # Debug: Show final results
        with st.expander("Debug: Final Results", expanded=True):
            st.write("Results:", results)
        
        return results
        
    except Exception as e:
        st.error(f"Error analyzing release notes with Ollama: {str(e)}")
        st.error("Full error details:", exc_info=True)
        return {
            'user': [],
            'admin': [],
            'compatibility': []
        }

def importance_badge(importance: str) -> str:
    """Create an HTML-styled badge for importance level."""
    colors = {
        'major': '#F6C344',
        'minor': '#4C9AFF'
    }
    return f"""<span style="
        background-color: {colors.get(importance.lower(), '#4C9AFF')};
        color: black;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    ">{importance}</span>"""

def warning_text(text: str) -> str:
    """Format warning text in red."""
    return f'<span style="color: #FF5630">{text}</span>'

def generate_markdown(results: Dict[str, Any], plugin_name: str, current_version: str, target_version: str) -> str:
    """Generate a markdown report from the analysis results."""
    markdown = f"# {plugin_name} Release Notes Analysis\n\n"
    markdown += f"Analysis from version {current_version} to {target_version}\n"
    markdown += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Add User Changes
    markdown += "## 👤 User Changes\n\n"
    user_changes_by_category = {}
    for change in results['user']:
        category = change.get('category', 'General')
        if category not in user_changes_by_category:
            user_changes_by_category[category] = []
        user_changes_by_category[category].append(change)
    
    for category, changes in user_changes_by_category.items():
        if category != 'General':
            markdown += f"### {category}\n\n"
        for change in changes:
            importance = "🔴" if change["importance"] == "major" else "🟡"
            markdown += f"{importance} {change['text']}\n\n"

    # Add Admin Changes
    markdown += "## ⚙️ Admin Changes\n\n"
    admin_changes_by_category = {}
    for change in results['admin']:
        category = change.get('category', 'General')
        if category not in admin_changes_by_category:
            admin_changes_by_category[category] = []
        admin_changes_by_category[category].append(change)
    
    for category, changes in admin_changes_by_category.items():
        if category != 'General':
            markdown += f"### {category}\n\n"
        for change in changes:
            importance = "🔴" if change["importance"] == "major" else "🟡"
            markdown += f"{importance} {change['text']}\n\n"

    # Add Compatibility Warnings
    if results['compatibility']:
        markdown += "## ⚠️ Compatibility Warnings\n\n"
        for warning in results['compatibility']:
            markdown += f"- ⚠️ {warning['text']}\n\n"

    return markdown

def generate_pdf(results: Dict[str, Any], plugin_name: str, current_version: str, target_version: str) -> bytes:
    """Generate a PDF report from the analysis results."""
    pdf = FPDF()
    pdf.add_page()
    
    # Set up fonts and margins
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_font('DejaVu', '', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    
    # Title
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(0, 10, f"{plugin_name} Release Notes Analysis", ln=True)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(0, 10, f"Analysis from version {current_version} to {target_version}", ln=True)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    # Helper function to write text with proper wrapping
    def write_change(text: str, importance: str = None):
        if importance == 'major':
            indicator = '[MAJOR] '
        elif importance == 'minor':
            indicator = '[MINOR] '
        else:
            indicator = '[!] '
        
        full_text = indicator + text
        pdf.multi_cell(0, 7, full_text)
        pdf.ln(3)

    # User Changes
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(0, 10, "User Changes", ln=True)
    pdf.ln(5)
    
    user_changes_by_category = {}
    for change in results['user']:
        category = change.get('category', 'General')
        if category not in user_changes_by_category:
            user_changes_by_category[category] = []
        user_changes_by_category[category].append(change)
    
    for category, changes in user_changes_by_category.items():
        if category != 'General':
            pdf.set_font('DejaVu', '', 12)
            pdf.cell(0, 10, category, ln=True)
        pdf.set_font('DejaVu', '', 10)
        for change in changes:
            write_change(change['text'], change['importance'])
        pdf.ln(5)

    # Admin Changes
    pdf.add_page()
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(0, 10, "Admin Changes", ln=True)
    pdf.ln(5)
    
    admin_changes_by_category = {}
    for change in results['admin']:
        category = change.get('category', 'General')
        if category not in admin_changes_by_category:
            admin_changes_by_category[category] = []
        admin_changes_by_category[category].append(change)
    
    for category, changes in admin_changes_by_category.items():
        if category != 'General':
            pdf.set_font('DejaVu', '', 12)
            pdf.cell(0, 10, category, ln=True)
        pdf.set_font('DejaVu', '', 10)
        for change in changes:
            write_change(change['text'], change['importance'])
        pdf.ln(5)

    # Compatibility Warnings
    if results['compatibility']:
        pdf.add_page()
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, "Compatibility Warnings", ln=True)
        pdf.ln(5)
        pdf.set_font('DejaVu', '', 10)
        
        for warning in results['compatibility']:
            write_change(warning['text'])
            pdf.ln(3)

    return bytes(pdf.output())

def display_analysis_results(results: Dict[str, Any], plugin_name: str, current_version: str, target_version: str):
    """Display analysis results in a table format with badges."""
    st.markdown("## Analysis Results")
    
    # Export buttons in the top right
    col1, col2, col3 = st.columns([6, 2, 2])
    
    # Only show export buttons if we have results
    if results['user'] or results['admin'] or results['compatibility']:
        with col2:
            # Generate and offer PDF download
            pdf_bytes = generate_pdf(results, plugin_name, current_version, target_version)
            st.download_button(
                "Export PDF",
                pdf_bytes,
                f"{plugin_name.lower().replace(' ', '_')}_analysis.pdf",
                "application/pdf",
                use_container_width=True
            )
        
        with col3:
            # Generate and offer Markdown download
            markdown_content = generate_markdown(results, plugin_name, current_version, target_version)
            st.download_button(
                "Export Markdown",
                markdown_content,
                f"{plugin_name.lower().replace(' ', '_')}_analysis.md",
                "text/markdown",
                use_container_width=True
            )

    # Create three columns for the table
    st.markdown("""
    <style>
    .analysis-header {
        color: #6B778C;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    .change-item {
        margin-bottom: 0.8rem;
    }
    .subsection-header {
        color: #172B4D;
        font-size: 1rem;
        margin: 1rem 0 0.5rem 0;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    cols = st.columns([4, 4, 4])
    
    # Headers
    cols[0].markdown('<p class="analysis-header">👤 User Changes</p>', unsafe_allow_html=True)
    cols[1].markdown('<p class="analysis-header">⚙️ Admin Changes</p>', unsafe_allow_html=True)
    cols[2].markdown('<p class="analysis-header">⚠️ Compatibility Warnings</p>', unsafe_allow_html=True)
    
    # Group user changes by category
    user_changes_by_category = {}
    for change in results['user']:
        category = change.get('category', 'General')
        if category not in user_changes_by_category:
            user_changes_by_category[category] = []
        user_changes_by_category[category].append(change)
    
    # Display User Changes
    for category, changes in user_changes_by_category.items():
        if category != 'General':
            cols[0].markdown(f'<p class="subsection-header">{category}</p>', unsafe_allow_html=True)
        for change in changes:
            cols[0].markdown(
                f'<div class="change-item">{importance_badge(change["importance"])}{change["text"]}</div>', 
                unsafe_allow_html=True
            )
    
    # Group admin changes by category
    admin_changes_by_category = {}
    for change in results['admin']:
        category = change.get('category', 'General')
        if category not in admin_changes_by_category:
            admin_changes_by_category[category] = []
        admin_changes_by_category[category].append(change)
    
    # Display Admin Changes
    for category, changes in admin_changes_by_category.items():
        if category != 'General':
            cols[1].markdown(f'<p class="subsection-header">{category}</p>', unsafe_allow_html=True)
        for change in changes:
            cols[1].markdown(
                f'<div class="change-item">{importance_badge(change["importance"])}{change["text"]}</div>', 
                unsafe_allow_html=True
            )
    
    # Display Compatibility Warnings
    for warning in results['compatibility']:
        cols[2].markdown(
            f'<div class="change-item">{warning_text(warning["text"])}</div>', 
            unsafe_allow_html=True
        )

def main():
    st.title("🚀 Jira Plugin Release Notes Analyzer (Local)")
    st.markdown("Analyze plugin release notes efficiently before upgrading Jira Data Center.")

    # Add model selection in sidebar
    with st.sidebar:
        st.header("Settings")
        model = st.selectbox(
            "Select Ollama Model",
            options=['mistral', 'llama3.2'],
            index=0,
            help="Choose a model for analysis. Mistral is recommended for best performance."
        )
        st.session_state['ollama_model'] = model
        
        if model == 'mistral':
            st.info("✨ Using Mistral for optimal performance")
        else:
            st.info("🦙 Using Llama3.2 for general analysis")

    # Jira Version Inputs
    col1, col2 = st.columns(2)
    with col1:
        current_jira_version = st.text_input("Current Jira Data Center Version", "9.4.0")
    with col2:
        target_jira_version = st.text_input("Target Jira Data Center Version", "10.3.0")

    # Plugin Configuration Section
    st.subheader("Plugin Configuration")

    # Create a form for plugin details
    with st.form("plugin_form"):
        plugin_name = st.text_input("Plugin Name")
        current_version = st.text_input("Current Version")
        target_version = st.text_input("Target Version")
        
        # URL inputs
        st.subheader("Release Notes URLs (up to 3)")
        url1 = st.text_input("Release Notes URL 1")
        url2 = st.text_input("Release Notes URL 2 (optional)")
        url3 = st.text_input("Release Notes URL 3 (optional)")
        
        # File upload
        st.subheader("Or Upload Release Notes File")
        uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
        
        # Submit button
        submitted = st.form_submit_button("Analyze Release Notes")

    # Process the inputs when form is submitted
    if submitted:
        st.info("Processing release notes...")
        
        all_text = ""
        
        # Process URLs
        urls = [url for url in [url1, url2, url3] if url]
        if urls:
            for url in urls:
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    all_text += soup.get_text() + "\n\n"
                except Exception as e:
                    st.error(f"Error fetching URL {url}: {str(e)}")
        
        # Process PDF if uploaded
        if uploaded_file:
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                for page in pdf_reader.pages:
                    all_text += page.extract_text() + "\n\n"
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
        
        if all_text:
            # Analyze the content using Ollama
            results = analyze_with_ollama(
                all_text,
                plugin_name or "Unknown Plugin",
                current_jira_version,
                target_jira_version
            )
            
            # Display results in the new format
            display_analysis_results(results, plugin_name or "Unknown Plugin", current_jira_version, target_jira_version)
        else:
            st.warning("No content to analyze. Please provide either URLs or a PDF file.")

if __name__ == "__main__":
    main() 