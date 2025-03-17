import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Jira Plugin Release Notes Analyzer",
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
from openai import OpenAI
from models import PluginAnalysis, ReleaseNote, ChangeType, Importance
from dotenv import load_dotenv

# Initialize environment and OpenAI client
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# Debug information in expandable section
with st.expander("Debug Information", expanded=False):
    st.write(f"Current working directory: {os.getcwd()}")
    st.write("Checking OpenAI API key...")
    if not api_key:
        st.error("OpenAI API key not found in environment variables.")
        st.error("Please ensure your .env file exists and contains OPENAI_API_KEY=your_key_here")
        st.stop()
    else:
        st.success("OpenAI API key found!")

    try:
        client = OpenAI(api_key=api_key)
        st.success("OpenAI client initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {str(e)}")
        st.stop()

SYSTEM_PROMPT = """You are a Jira plugin release notes analyzer. Your task is to analyze release notes and provide a concise, structured summary of the most important changes.

Focus on these key areas:
1. Major user-facing changes (new features, significant UI changes, important bug fixes)
2. Critical admin/technical changes (security updates, performance improvements, configuration changes)
3. Compatibility information (Jira version compatibility, breaking changes, deprecations)

For each change:
- Extract the version number
- Determine if it's a major or minor change
- Provide a clear, concise description
- Remove any redundant information
- Skip minor bug fixes unless they're significant
- Combine similar changes into single items
- Keep only the most important changes (max 5-7 per category)

Here's an example of the expected output format:

Admin Changes:
Jira Compatibility:
• Versions 8.22.0 through 8.32.0 introduce compatibility with Jira versions 9.13.x to 9.17.x
• Version 9.1.1 introduces compatibility with Jira 10.0
• Versions 9.5.0 and 9.7.0 introduce compatibility with Jira versions 10.1.x and 10.3.0

Security Improvements:
• Version 9.4.0 includes a resources update to remove password visibility
• Version 9.6.0 addresses a known Common Vulnerabilities and Exposures (CVE)
• Version 8.34.0 fixes a vulnerability related to the Switch User feature

Configuration Changes:
• Version 9.5.0 introduces compatibility with Configuration Manager for Jira
• Version 9.1.1 requires specific configuration for Tempo compatibility

User Changes:
New Features:
• Version 8.20.0 introduces a new Duplicate feature for Fragments and Vendors API updates
• Version 8.21.0 updates the Script Editor page with new Example Scripts button
• Version 8.32.0 adds Library script for field values and workflow function improvements
• Version 9.3.0 adds method to recalculate Scripted Field values

Important Bug Fixes:
• Version 8.34.0 fixes Behaviors breaking in Chrome v127 and Edge v127
• Multiple versions address critical user experience issues

Compatibility Warnings:
• Jira 10 Compatibility: ScriptRunner 9.1.1 or later required
• Tempo Compatibility: Version 9.1.1 incompatible with Tempo after Jira 10.0 upgrade
• Breaking Changes: Jira 10 upgrade requires script updates
• UI Fragments: Jira 10 introduces changes requiring fragment adjustments

Follow this example format but adapt it to the specific content of the release notes being analyzed."""

USER_PROMPT_TEMPLATE = """Analyze these release notes and provide a structured summary:

Current Jira Version: {current_version}
Target Jira Version: {target_version}
Plugin: {plugin_name}

Release Notes:
{release_notes}

Analyze the release notes and provide a summary following exactly the same format as shown in the system prompt example. Focus on the most important changes between the current and target versions, with special attention to compatibility issues and breaking changes."""

def analyze_with_openai(text: str, plugin_name: str, current_version: str, target_version: str) -> Dict[str, List[Dict[str, Any]]]:
    """Use OpenAI to analyze the release notes."""
    try:
        # Prepare the prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            current_version=current_version,
            target_version=target_version,
            plugin_name=plugin_name,
            release_notes=text
        )

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=2000
        )

        # Parse the response
        analysis_text = response.choices[0].message.content
        
        results = {
            'user': [],
            'admin': [],
            'compatibility': []
        }
        
        # Split into main sections
        sections = analysis_text.split('\n\n')
        current_main_section = None
        current_subsection = None
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for main sections
                if line == 'Admin Changes:':
                    current_main_section = 'admin'
                    current_subsection = None
                elif line == 'User Changes:':
                    current_main_section = 'user'
                    current_subsection = None
                elif line == 'Compatibility Warnings:':
                    current_main_section = 'compatibility'
                    current_subsection = None
                # Check for subsections
                elif line.endswith(':'):
                    current_subsection = line[:-1]  # Remove the colon
                # Process actual content
                elif line.startswith('•'):
                    content = line[2:].strip()  # Remove bullet point
                    
                    # Extract version if present
                    version_match = re.search(r'Version[s]?\s+([\d\., ]+(?:through|and)\s+[\d\.]+|[\d\.]+)', content)
                    version = version_match.group(1) if version_match else 'N/A'
                    
                    # Determine importance based on content and section
                    importance = 'major' if any(word in content.lower() for word in 
                        ['security', 'vulnerability', 'breaking', 'compatibility', 'critical']) else 'minor'
                    
                    if current_main_section == 'compatibility':
                        results['compatibility'].append({
                            'text': content
                        })
                    else:
                        item = {
                            'importance': importance,
                            'text': content,
                            'version': version,
                            'category': current_subsection or 'General'
                        }
                        if current_main_section:
                            results[current_main_section].append(item)
        
        return results
        
    except Exception as e:
        st.error(f"Error analyzing release notes with OpenAI: {str(e)}")
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

def display_analysis_results(results: Dict[str, Any], plugin_name: str):
    """Display analysis results in a table format with badges."""
    st.markdown("## Analysis Results")
    
    # Export button in the top right
    col1, col2 = st.columns([8, 2])
    with col2:
        st.download_button(
            "Export CSV",
            "TODO: Implement CSV export",
            "analysis_results.csv",
            "text/csv",
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
    
    cols = st.columns([2, 4, 4, 4])
    
    # Headers
    cols[0].markdown('<p class="analysis-header">Plugin</p>', unsafe_allow_html=True)
    cols[1].markdown('<p class="analysis-header">User Changes</p>', unsafe_allow_html=True)
    cols[2].markdown('<p class="analysis-header">Admin Changes</p>', unsafe_allow_html=True)
    cols[3].markdown('<p class="analysis-header">Compatibility Warnings</p>', unsafe_allow_html=True)
    
    # Plugin name in first column
    cols[0].markdown(f"**{plugin_name}**")
    
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
            cols[1].markdown(f'<p class="subsection-header">{category}</p>', unsafe_allow_html=True)
        for change in changes:
            cols[1].markdown(
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
            cols[2].markdown(f'<p class="subsection-header">{category}</p>', unsafe_allow_html=True)
        for change in changes:
            cols[2].markdown(
                f'<div class="change-item">{importance_badge(change["importance"])}{change["text"]}</div>', 
                unsafe_allow_html=True
            )
    
    # Display Compatibility Warnings
    for warning in results['compatibility']:
        cols[3].markdown(
            f'<div class="change-item">{warning_text(warning["text"])}</div>', 
            unsafe_allow_html=True
        )

st.title("🚀 Jira Plugin Release Notes Analyzer")
st.markdown("Analyze plugin release notes efficiently before upgrading Jira Data Center.")

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
        # Analyze the content using OpenAI
        results = analyze_with_openai(
            all_text,
            plugin_name or "Unknown Plugin",
            current_jira_version,
            target_jira_version
        )
        
        # Display results in the new format
        display_analysis_results(results, plugin_name or "Unknown Plugin")
    else:
        st.warning("No content to analyze. Please provide either URLs or a PDF file.")

# Add export functionality
if st.button("Export Report"):
    st.info("Export functionality will be implemented in the next iteration")
