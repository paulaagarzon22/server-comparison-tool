import streamlit as st
import pandas as pd
import sqlite3
import json
import hashlib
import re
import os
from typing import List, Dict, Any

# Database configuration
DB_FILE = os.path.join(os.path.dirname(__file__), 'companies_data.db')

# Page configuration
st.set_page_config(
    page_title="Server Configuration Comparison Tool",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Sidebar styling - darker blue-gray */
    [data-testid="stSidebar"] {
        background-color: #2c3e50;
    }
    
    /* Sidebar text styling - white text (excluding select boxes) */
    [data-testid="stSidebar"] > div > div > div > div {
        color: white !important;
    }
    
    /* Sidebar headers and labels - white text */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: white !important;
    }
    
    /* Select box - keep text black inside white boxes */
    [data-testid="stSidebar"] .stSelect {
        color: black !important;
    }
    
    [data-testid="stSidebar"] .stSelect > div {
        color: black !important;
    }
    
    [data-testid="stSidebar"] .stSelect > div > div {
        color: black !important;
    }
    
    [data-testid="stSidebar"] .stSelect > div > div > div {
        color: black !important;
    }
    
    [data-testid="stSidebar"] .stSelect > div > div > div > div {
        color: black !important;
    }
    
    [data-testid="stSidebar"] .stSelect > div > div > div > div > div {
        color: black !important;
    }
    
    /* Select box options - black text */
    [data-testid="stSidebar"] .stSelect option {
        color: black !important;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: left;
        margin-bottom: 2rem;
        margin-top: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .comparison-table {
        margin-top: 1rem;
    }
    .gap-analysis {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
    }
    /* Hardware list styling */
    ul {
        margin: 8px 0;
        padding-left: 20px;
        line-height: 1.8;
    }
    li {
        margin-bottom: 8px;
        padding-left: 8px;
    }
    /* Full-width horizontal separators between comparison rows */
    hr {
        border: none;
        border-top: 2px solid #E0E0E0;
        margin: 0.5rem 0;
    }
    /* Improved comparison column styling */
    .stColumns > div {
        gap: 0.5rem;
    }
    /* Better text wrapping for long content */
    div[data-testid="stVerticalBlock"] > div > div > div > div {
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

def get_all_data() -> Dict[str, pd.DataFrame]:
    """Load all data from database into DataFrames"""
    conn = sqlite3.connect(DB_FILE)
    
    # Get all table names
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    
    data = {}
    for table in tables:
        df = pd.read_sql(f"SELECT * FROM '{table}'", conn)
        data[table] = df
    
    conn.close()
    return data

def parse_json_column(value):
    """Parse JSON columns that contain bullet point lists"""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except:
            return value
    return value

def format_display_value(value):
    """Format values for display in the UI"""
    if value is None:
        return "N/A"
    if isinstance(value, list):
        # Remove bullet points only at the beginning to avoid breaking legitimate text
        clean_items = []
        for item in value:
            item_str = str(item).strip()
            if item_str.startswith('•'):
                item_str = item_str[1:].strip()
            elif item_str.startswith('*'):
                item_str = item_str[1:].strip()
            # Check if the item is now just "A" or empty after bullet removal
            if item_str == 'A' or item_str == 'a' or item_str == '':
                continue  # Skip empty items or standalone "A"
            clean_items.append(item_str)
        # Always format as HTML list for consistent styling, even with single items
        list_items = [f"<li>{str(item)}</li>" for item in clean_items]
        return f"<ul>{''.join(list_items)}</ul>"
    # Convert single string to list for consistent formatting
    clean_value = str(value).strip()
    if clean_value.startswith('•'):
        clean_value = clean_value[1:].strip()
    elif clean_value.startswith('*'):
        clean_value = clean_value[1:].strip()
    # Check if the item is now just "A" or empty after bullet removal
    if clean_value == 'A' or clean_value == 'a' or clean_value == '':
        clean_value = "N/A"
    list_items = [f"<li>{clean_value}</li>"]
    return f"<ul>{''.join(list_items)}</ul>"

def display_list_with_show_more(value, key_prefix):
    """Display list with show more functionality using proper HTML list styling"""
    if value is None:
        st.write("N/A")
        return
    if not isinstance(value, list):
        # Convert single string to list for consistent formatting
        value = [str(value)]
    
    # Separate summary lines from configuration options
    summary_lines = []
    config_options = []
    
    for item in value:
        item_str = str(item).strip()
        # Remove bullet points only at the beginning to avoid breaking legitimate text
        if item_str.startswith('•'):
            item_str = item_str[1:].strip()
        elif item_str.startswith('*'):
            item_str = item_str[1:].strip()
        # Check if the item is now just "A" or empty after bullet removal
        if item_str == 'A' or item_str == 'a' or item_str == '':
            continue  # Skip empty items or standalone "A"
        if item_str.startswith("[Summary:"):
            summary_lines.append(item_str)
        elif item_str.startswith("[Storage]"):
            # Remove [Storage] prefix and add to config options
            clean_item = item_str.replace("[Storage]", "").strip()
            config_options.append(clean_item)
        else:
            # Keep as is for other categories
            config_options.append(item_str)
    
    # Display summary lines outside of bullet list
    for summary in summary_lines:
        st.markdown(f"**{summary}**")
    
    # Convert config options to HTML list elements
    list_items = [f"<li>{str(item)}</li>" for item in config_options]
    
    # Format as HTML list for consistent styling
    if len(config_options) <= 5:
        # Show all items
        html_list = f"<ul>{''.join(list_items)}</ul>"
        st.markdown(html_list, unsafe_allow_html=True)
    else:
        # Show first 5 items with show more functionality
        html_list = f"<ul>{''.join(list_items[:5])}</ul>"
        st.markdown(html_list, unsafe_allow_html=True)
        
        show_more_key = f"show_more_{key_prefix}"
        
        # Initialize session state if not exists
        if show_more_key not in st.session_state:
            st.session_state[show_more_key] = False
        
        if st.session_state[show_more_key]:
            # Show all items
            html_list = f"<ul>{''.join(list_items)}</ul>"
            st.markdown(html_list, unsafe_allow_html=True)
            if st.button("Show less", key=f"less_{key_prefix}"):
                st.session_state[show_more_key] = False
                st.rerun()
        else:
            if st.button(f"Show more ({len(config_options) - 5} more)", key=f"more_{key_prefix}"):
                st.session_state[show_more_key] = True
                st.rerun()

def display_list_with_show_more_compact(value, key_prefix):
    """Display list with show more functionality in compact format for comparison columns"""
    if value is None:
        st.write("N/A")
        return
    if not isinstance(value, list):
        # Convert single string to list for consistent formatting
        value = [str(value)]
    
    # Separate summary lines from configuration options
    summary_lines = []
    config_options = []
    
    for item in value:
        item_str = str(item).strip()
        # Remove bullet points only at the beginning to avoid breaking legitimate text
        if item_str.startswith('•'):
            item_str = item_str[1:].strip()
        elif item_str.startswith('*'):
            item_str = item_str[1:].strip()
        # Check if the item is now just "A" or empty after bullet removal
        if item_str == 'A' or item_str == 'a' or item_str == '':
            continue  # Skip empty items or standalone "A"
        if item_str.startswith("[Summary:"):
            summary_lines.append(item_str)
        elif item_str.startswith("[Storage]"):
            # Remove [Storage] prefix and add to config options
            clean_item = item_str.replace("[Storage]", "").strip()
            config_options.append(clean_item)
        else:
            # Keep as is for other categories
            config_options.append(item_str)
    
    # Display summary lines
    for summary in summary_lines:
        st.markdown(f"*{summary}*")
    
    # Display configuration options as bullet list
    if config_options:
        # Always format as HTML list for consistent styling, even with single items
        if len(config_options) <= 3:  # Show fewer items in compact view
            # Show all items as a proper HTML list with increased font size
            list_items = [f"<li>{str(item)}</li>" for item in config_options]
            html_list = f"<ul style='margin: 0; padding-left: 20px; font-size: 16px; line-height: 1.6;'>{''.join(list_items)}</ul>"
            st.markdown(html_list, unsafe_allow_html=True)
        else:
            show_more_key = f"show_more_{key_prefix}"
            
            # Initialize session state if not exists
            if show_more_key not in st.session_state:
                st.session_state[show_more_key] = False
            
            if st.session_state[show_more_key]:
                # Show all items as a proper HTML list with increased font size
                list_items = [f"<li>{str(item)}</li>" for item in config_options]
                html_list = f"<ul style='margin: 0; padding-left: 20px; font-size: 16px; line-height: 1.6;'>{''.join(list_items)}</ul>"
                st.markdown(html_list, unsafe_allow_html=True)
                if st.button("Show less", key=f"less_{key_prefix}"):
                    st.session_state[show_more_key] = False
                    st.rerun()
            else:
                # Show first 3 items as a proper HTML list with increased font size
                list_items = [f"<li>{str(item)}</li>" for item in config_options[:3]]
                html_list = f"<ul style='margin: 0; padding-left: 20px; font-size: 16px; line-height: 1.6;'>{''.join(list_items)}</ul>"
                st.markdown(html_list, unsafe_allow_html=True)
                if st.button(f"Show {len(config_options) - 3} more", key=f"more_{key_prefix}"):
                    st.session_state[show_more_key] = True
                    st.rerun()

def display_server_details(row, key_prefix):
    """Display server details using specification matrix layout"""
    server_type = row.get('Server Type', 'Unknown')
    
    # Display basic information header
    st.markdown(f"""
    <div style='border: 2px solid #ddd; padding: 15px; border-radius: 5px; margin-bottom: 20px; background-color: #f9f9f9;'>
        <div style='font-size: 18px; font-weight: bold; margin-bottom: 10px;'>Product: {format_product_name_for_display(row)}</div>
        <div style='font-size: 14px;'><strong>Company:</strong> {row['Company']}</div>
        <div style='font-size: 14px;'><strong>Server Type:</strong> {server_type}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Define specification categories
    categories = [
        ('CPU', row.get('CPU', 'N/A')),
        ('GPU', row.get('GPU', 'N/A')),
        ('Memory', row.get('Memory', 'N/A')),
        ('Storage Drive Type', row.get('Storage Drive Type', 'N/A')),
        ('Max Configuration', row.get('Max Drive Configuration', 'N/A'))
    ]
    
    # Create specification matrix using Streamlit columns
    for category, value in categories:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"**{category}**")
        with col2:
            display_list_with_show_more(value, f"{category.lower()}_{key_prefix}")
        st.markdown("---")

def display_server_details_compact(row, key_prefix):
    """Display server details in compact format for side-by-side comparison"""
    server_type = row.get('Server Type', 'Unknown')
    
    # Display basic information in compact format
    st.markdown(f"""
    <div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: #f9f9f9;'>
        <div style='font-size: 14px; font-weight: bold;'>{format_product_name_for_display(row)}</div>
        <div style='font-size: 12px;'>{row['Company']}</div>
        <div style='font-size: 12px;'>{server_type}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Define specification categories
    categories = [
        ('CPU', row.get('CPU', 'N/A')),
        ('GPU', row.get('GPU', 'N/A')),
        ('Memory', row.get('Memory', 'N/A')),
        ('Storage Drive Type', row.get('Storage Drive Type', 'N/A')),
        ('Max Configuration', row.get('Max Drive Configuration', 'N/A'))
    ]
    
    # Create compact specification display
    for category, value in categories:
        st.markdown(f"**{category}**")
        display_list_with_show_more_compact(value, f"{category.lower()}_{key_prefix}")
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

def display_storage_subcategories(row, key_prefix):
    """Display storage subcategories within a single cell for Supermicro and Lenovo"""
    subcategories = [
        ('HDD', 'Storage HDD'),
        ('SAS SSD', 'Storage SAS SSD'),
        ('SATA SSD', 'Storage SATA SSD'),
        ('M.2 SSD', 'Storage M.2 SSD'),
        ('NVMe SSD', 'Storage NVMe SSD'),
    ]
    
    html_content = "<div style='margin: 0; padding: 0;'>"
    has_subcategories = False
    
    for label, col_name in subcategories:
        value = row.get(col_name, None)
        if value and value != 'N/A':
            # Parse the value if it's a string representation of a list
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except:
                    value = [value]
            
            if value and len(value) > 0:
                has_subcategories = True
                html_content += f"<div style='margin-bottom: 8px;'>"
                html_content += f"<strong style='font-size: 16px; color: #2c3e50;'>{label}:</strong><br/>"
                
                # Create HTML list with same styling as standard bullet points
                list_items = []
                for item in value[:5]:
                    item_str = str(item).strip()
                    # Remove prefix if present (handle both Supermicro and Lenovo formats)
                    if item_str.startswith('HDD:'):
                        item_str = item_str[4:].strip()
                    elif item_str.startswith('SAS SSD:'):
                        item_str = item_str[8:].strip()
                    elif item_str.startswith('SATA SSD:'):
                        item_str = item_str[9:].strip()
                    elif item_str.startswith('M.2 SSD:'):
                        item_str = item_str[8:].strip()
                    elif item_str.startswith('M.2:'):
                        item_str = item_str[4:].strip()
                    elif item_str.startswith('NVMe SSD:'):
                        item_str = item_str[8:].strip()
                    elif item_str.startswith('NVMe:'):
                        item_str = item_str[5:].strip()
                    elif item_str.startswith('E3.S:'):
                        item_str = item_str[5:].strip()
                    elif item_str.startswith('SSD:'):
                        item_str = item_str[4:].strip()
                    # Remove bullet point if present at the start
                    if item_str.startswith('•'):
                        item_str = item_str[1:].strip()
                    # Remove leading colon if present
                    if item_str.startswith(':'):
                        item_str = item_str[1:].strip()
                    
                    list_items.append(f"<li>{item_str}</li>")
                
                # Use same styling as display_list_with_show_more_compact
                html_list = f"<ul style='margin: 0; padding-left: 20px; font-size: 16px; line-height: 1.6;'>{''.join(list_items)}</ul>"
                html_content += html_list
                
                # Show more button if needed
                if len(value) > 5:
                    show_more_key = f"storage_{col_name}_{key_prefix}"
                    
                    # Initialize session state if not exists
                    if show_more_key not in st.session_state:
                        st.session_state[show_more_key] = False
                    
                    if st.session_state[show_more_key]:
                        # Show all items
                        more_list_items = []
                        for item in value[5:]:
                            item_str = str(item).strip()
                            # Remove prefix if present (handle both Supermicro and Lenovo formats)
                            if item_str.startswith('HDD:'):
                                item_str = item_str[4:].strip()
                            elif item_str.startswith('SAS SSD:'):
                                item_str = item_str[8:].strip()
                            elif item_str.startswith('SATA SSD:'):
                                item_str = item_str[9:].strip()
                            elif item_str.startswith('M.2 SSD:'):
                                item_str = item_str[8:].strip()
                            elif item_str.startswith('M.2:'):
                                item_str = item_str[4:].strip()
                            elif item_str.startswith('NVMe SSD:'):
                                item_str = item_str[8:].strip()
                            elif item_str.startswith('NVMe:'):
                                item_str = item_str[5:].strip()
                            elif item_str.startswith('E3.S:'):
                                item_str = item_str[5:].strip()
                            elif item_str.startswith('SSD:'):
                                item_str = item_str[4:].strip()
                            # Remove bullet point if present at the start
                            if item_str.startswith('•'):
                                item_str = item_str[1:].strip()
                            # Remove leading colon if present
                            if item_str.startswith(':'):
                                item_str = item_str[1:].strip()
                            
                            more_list_items.append(f"<li>{item_str}</li>")
                        
                        html_list = f"<ul style='margin: 0; padding-left: 20px; font-size: 16px; line-height: 1.6;'>{''.join(list_items + more_list_items)}</ul>"
                        st.markdown(html_list, unsafe_allow_html=True)
                        if st.button("Show less", key=f"less_{show_more_key}"):
                            st.session_state[show_more_key] = False
                            st.rerun()
                        html_content = ""  # Clear html_content since we already rendered
                    else:
                        st.markdown(html_content, unsafe_allow_html=True)
                        if st.button(f"Show {len(value) - 5} more", key=f"more_{show_more_key}"):
                            st.session_state[show_more_key] = True
                            st.rerun()
                        html_content = ""  # Clear html_content since we already rendered
                else:
                    st.markdown(html_content, unsafe_allow_html=True)
                    html_content = ""  # Clear html_content since we already rendered
                
                if html_content:
                    html_content += "</div>"
    
    if html_content:
        html_content += "</div>"
        st.markdown(html_content, unsafe_allow_html=True)
    
    # If no subcategories found, fall back to standard display
    if not has_subcategories:
        original_storage = row.get('Storage Drive Type', 'N/A')
        display_list_with_show_more_compact(original_storage, f"storage_fallback_{key_prefix}")

def display_comparison_matrix(vendors, key_prefix):
    """Display server specs as a row-aligned comparison matrix.
    
    vendors: list of dicts with keys: company, product, row, color, found
    key_prefix: base string used to generate unique Show More keys
    """
    # Check if any vendor is Supermicro (has storage sub-categories)
    has_supermicro = any(vendor['company'] == 'Supermicro' for vendor in vendors)
    
    # Use single storage category for all, with special formatting for Supermicro
    categories = [
        ('CPU', 'CPU'),
        ('GPU', 'GPU'),
        ('Memory', 'Memory'),
        ('Drive Type', 'Storage Drive Type'),
        ('Max Configuration', 'Max Drive Configuration'),
    ]
    
    # Header row with improved styling and better spacing (no Category label)
    header_container = st.container()
    with header_container:
        header_cols = st.columns([1.0] + [4.0] * len(vendors))
        header_cols[0].empty()  # Empty space instead of "Category" label
        for i, vendor in enumerate(vendors):
            with header_cols[i + 1]:
                color = vendor.get('color', '#1f77b4')
                server_type = vendor.get('server_type', '')
                server_type_html = f"<div style='font-size: 14px; color: #666; margin-top: 4px; text-align: center;'>{server_type}</div>" if server_type else ""
                # Add company qualifier if there are multiple competitors from same company
                company_name = vendor['company']
                product_name = vendor['product']
                
                # Check if there are multiple vendors from the same company
                company_count = sum(1 for v in vendors if v['company'] == company_name)
                if company_count > 1:
                    # Add qualifier like "Lenovo 1", "Lenovo 2" etc.
                    company_index = sum(1 for v in vendors[:i] if v['company'] == company_name) + 1
                    company_name = f"{company_name} {company_index}"
                
                st.markdown(
                    f"<div style='text-align: center;'>"
                    f"<div style='font-size: 24px; font-weight: bold; color: {color}; margin-bottom: 4px;'>{company_name}</div>"
                    f"<div style='font-size: 17px; font-weight: 600; margin-bottom: 2px;'>{product_name}</div>"
                    f"{server_type_html}"
                    f"</div>",
                    unsafe_allow_html=True
                )
    
    st.markdown("---", unsafe_allow_html=True)
    
    # Category rows with improved spacing
    for j, (label, col_name) in enumerate(categories):
        cols = st.columns([1.0] + [4.0] * len(vendors))
        cols[0].markdown(f"**{label}**")
        for i, vendor in enumerate(vendors):
            with cols[i + 1]:
                if vendor.get('found', True) and vendor.get('row') is not None:
                    # Special handling for Drive Type with Supermicro and Lenovo subcategories
                    if label == 'Drive Type' and (vendor['company'] == 'Supermicro' or vendor['company'] == 'Lenovo'):
                        cell_key = re.sub(r'[^a-zA-Z0-9_]', '_', f"{key_prefix}_{i}_{j}")
                        display_storage_subcategories(vendor['row'], cell_key)
                    else:
                        value = vendor['row'].get(col_name, 'N/A')
                        cell_key = re.sub(r'[^a-zA-Z0-9_]', '_', f"{key_prefix}_{i}_{j}")
                        display_list_with_show_more_compact(value, cell_key)
                else:
                    st.markdown("*N/A*")
        st.markdown("---")

def format_supermicro_product_name(product_name):
    """Format Supermicro product names from arrays to hyphenated model numbers"""
    if isinstance(product_name, list):
        return "-".join(str(item) for item in product_name)
    elif isinstance(product_name, str):
        # Check if it's a JSON array string
        if product_name.startswith('[') and product_name.endswith(']'):
            try:
                import json
                parsed = json.loads(product_name)
                if isinstance(parsed, list):
                    return "-".join(str(item) for item in parsed)
            except:
                pass
        return product_name
    return product_name

def format_product_name_for_display(row):
    """Format product name for display, handling Supermicro arrays"""
    company = row.get('Company', '')
    product_name = row.get('Product Name', '')
    
    if company == 'Supermicro':
        return format_supermicro_product_name(product_name)
    return product_name

def normalize_supermicro_name(product_name):
    """Normalize Supermicro product name for comparison"""
    if isinstance(product_name, list):
        return "-".join(str(item) for item in product_name)
    elif isinstance(product_name, str):
        if '-' in product_name:
            return product_name
        if product_name.startswith('[') and product_name.endswith(']'):
            try:
                import json
                parsed = json.loads(product_name)
                if isinstance(parsed, list):
                    return "-".join(str(item) for item in parsed)
            except:
                pass
    return product_name

def get_company_from_table(table_name: str) -> str:
    """Extract company name from table name"""
    if 'lenovo' in table_name.lower():
        return 'Lenovo'
    elif 'supermicro' in table_name.lower():
        return 'Supermicro'
    elif 'dell' in table_name.lower():
        return 'Dell'
    else:
        return 'Unknown'

def get_server_type_from_table(table_name: str) -> str:
    """Extract server type from table name"""
    # Remove the company prefix
    if 'lenovo_data_' in table_name:
        return table_name.replace('lenovo_data_', '').replace('_', ' ').title()
    elif 'lenovo_configurations_' in table_name:
        return table_name.replace('lenovo_configurations_', '').replace('_', ' ').title()
    elif 'supermicro_configurations_final_' in table_name:
        return table_name.replace('supermicro_configurations_final_', '').replace('_', ' ').title()
    elif 'dell_configurations_' in table_name:
        return table_name.replace('dell_configurations_', '').replace('_', ' ').title()
    return table_name

def get_dell_server_type_from_mapping(product_name: str, mapping_df: pd.DataFrame) -> str:
    """Get Dell server type from mapping data"""
    try:
        if mapping_df is None or len(mapping_df) == 0:
            return "Unknown"
        
        # Find matching Dell server in mapping
        match = mapping_df[mapping_df['Dell Server'] == product_name]
        if len(match) > 0:
            return match.iloc[0]['Server Category']
        return "Unknown"
    except Exception:
        return "Unknown"

def hash_password(password: str) -> str:
    """Hash a password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password: str, hashed_password: str) -> bool:
    """Check if a password matches the hash"""
    return hash_password(password) == hashed_password

def show_login_page():
    """Display login page"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            border: 1px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .login-title {
            font-size: 2rem;
            color: #1f77b4;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">🔐 Login</h1>', unsafe_allow_html=True)
    st.markdown("Server Configuration Comparison Tool")
    st.markdown('</div>', unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials"""
    # Simple hardcoded credentials (in production, use a proper database)
    users = {
        'admin': hash_password('admin123'),
        'procurement': hash_password('procurement123'),
        'dell': hash_password('dell123')
    }
    
    return username in users and check_password(password, users[username])

def logout():
    """Logout user"""
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.rerun()

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    
    # Check authentication
    if not st.session_state['authenticated']:
        show_login_page()
        return
    
    # Main header with logout button
    col1, col2, col3 = st.columns([6, 2, 2])
    with col1:
        st.markdown('<h1 class="main-header">Server Configuration Comparison Tool</h1>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout"):
            logout()
    
    # Load data
    try:
        all_data = get_all_data()
        
        # Load server mapping data
        try:
            conn = sqlite3.connect(DB_FILE)
            mapping_df = pd.read_sql("SELECT * FROM server_mapping", conn)
            conn.close()
        except Exception:
            mapping_df = None
            st.warning("Server mapping data not available")
    except Exception as e:
        st.error(f"Error loading database: {e}")
        st.info("Please ensure 'companies_data.db' is in the same directory as this app.")
        return
    
    # Combine all data into a single DataFrame with company and server type info
    combined_data = []
    for table_name, df in all_data.items():
        # Skip the server_mapping table - it's only for reference, not for display
        if table_name == 'server_mapping':
            continue
            
        df_copy = df.copy()
        company = get_company_from_table(table_name)
        df_copy['Company'] = company
        
        # Skip tables with unknown company (like server_mapping)
        if company == 'Unknown':
            continue
        
        # For Dell servers, use mapping data for server type
        if company == 'Dell':
            try:
                df_copy['Server Type'] = df_copy['Product Name'].apply(
                    lambda x: get_dell_server_type_from_mapping(x, mapping_df)
                )
            except Exception as e:
                # Fallback to table-based server type if mapping fails
                df_copy['Server Type'] = get_server_type_from_table(table_name)
        else:
            df_copy['Server Type'] = get_server_type_from_table(table_name)
        
        df_copy['Table Source'] = table_name
        combined_data.append(df_copy)
    
    master_df = pd.concat(combined_data, ignore_index=True)
    
    # Parse JSON columns
    json_columns = ['CPU', 'GPU', 'Memory', 'Storage Drive Type', 'Max Drive Configuration', 'Storage Controller', 
                    'Storage HDD', 'Storage SAS SSD', 'Storage SATA SSD', 'Storage M.2 SSD', 'Storage NVMe SSD']
    for col in json_columns:
        if col in master_df.columns:
            master_df[col] = master_df[col].apply(parse_json_column)
    
    # Sidebar for filtering
    st.sidebar.header("Filters")
    
    # Company filter
    companies = ['All'] + sorted(master_df['Company'].unique().tolist())
    selected_company = st.sidebar.selectbox("Select Company", companies)
    
    # Server type filter
    server_types = ['All'] + sorted(master_df['Server Type'].unique().tolist())
    selected_server_type = st.sidebar.selectbox("Select Server Type", server_types)
    
    # Apply filters
    filtered_df = master_df.copy()
    if selected_company != 'All':
        filtered_df = filtered_df[filtered_df['Company'] == selected_company]
    if selected_server_type != 'All':
        filtered_df = filtered_df[filtered_df['Server Type'] == selected_server_type]
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["Catalog", "Dell Mapped Comparisons", "User Selected Comparisons"])
    
    # Tab 1: Catalog View
    with tab1:
        st.markdown('<h2 class="sub-header">Server Catalog</h2>', unsafe_allow_html=True)
        
        # Add search bar
        search_term = st.text_input("Search servers", "", placeholder="Search by product name, company, server type, CPU, GPU, etc.")
        
        # Apply search filter
        if search_term:
            search_term_lower = search_term.lower()
            search_df = filtered_df.copy()
            
            # Search across multiple columns
            def search_row(row):
                searchable_text = ""
                for col in ['Company', 'Product Name', 'Server Type', 'CPU', 'GPU', 'Memory']:
                    if col in row.index:
                        value = row[col]
                        try:
                            if pd.isna(value):
                                continue
                        except:
                            continue
                        if isinstance(value, list):
                            searchable_text += " ".join(str(item) for item in value) + " "
                        else:
                            searchable_text += str(value) + " "
                return search_term_lower in searchable_text.lower()
            
            search_df = search_df[search_df.apply(search_row, axis=1)]
            
            if len(search_df) == 0:
                st.warning(f"No servers found matching search term: '{search_term}'")
                st.info("Try different keywords or clear the search to see all servers.")
            else:
                st.info(f"Showing {len(search_df)} server(s) matching '{search_term}'")
                # Display servers as cards
                for idx, row in search_df.iterrows():
                    server_type = row.get('Server Type', 'Unknown')
                    display_product_name = format_product_name_for_display(row)
                    with st.expander(f"{row['Company']} - {display_product_name} ({server_type})"):
                        display_server_details(row, f"search_{idx}")
        else:
            if len(filtered_df) == 0:
                st.warning("No servers found matching the selected filters.")
            else:
                st.info(f"Showing {len(filtered_df)} server(s)")
                
                # Display servers as cards
                for idx, row in filtered_df.iterrows():
                    server_type = row.get('Server Type', 'Unknown')
                    display_product_name = format_product_name_for_display(row)
                    with st.expander(f"{row['Company']} - {display_product_name} ({server_type})"):
                        display_server_details(row, idx)
    
    # Tab 3: User Selected Comparisons
    with tab3:
        st.markdown('<h2 class="sub-header">User Selected Comparisons</h2>', unsafe_allow_html=True)
        
        # Server selection for comparison
        st.subheader("Select Servers to Compare")
        
        # Get available servers for selection
        available_servers = filtered_df[['Company', 'Product Name', 'Server Type']].copy()
        available_servers['Display Name'] = available_servers.apply(
            lambda row: f"{row['Company']} - {format_product_name_for_display(row)}", 
            axis=1
        )
        
        # Multi-select for servers
        selected_servers = st.multiselect(
            "Choose up to 4 servers to compare",
            available_servers['Display Name'].tolist(),
            max_selections=4
        )
        
        if len(selected_servers) < 2:
            st.info("Please select at least 2 servers to compare.")
        else:
            # Get selected server data
            comparison_data = []
            for server_display in selected_servers:
                server_row = available_servers[available_servers['Display Name'] == server_display].iloc[0]
                server_data = filtered_df[
                    (filtered_df['Company'] == server_row['Company']) & 
                    (filtered_df['Product Name'] == server_row['Product Name'])
                ].iloc[0]
                comparison_data.append(server_data)
            
            # Build vendor list and display as a shared-row comparison matrix
            company_colors = {'Dell': '#0076CE', 'Lenovo': '#E2231A', 'Supermicro': '#28A745'}
            vendors = []
            for idx, server_data in enumerate(comparison_data):
                company = server_data['Company']
                product = format_product_name_for_display(server_data)
                server_type = server_data.get('Server Type', 'Unknown')
                color = company_colors.get(company, '#1f77b4')
                vendors.append({
                    'company': company,
                    'product': product,
                    'server_type': server_type,
                    'row': server_data,
                    'color': color,
                    'found': True
                })
            
            matrix_key = re.sub(r'[^a-zA-Z0-9_]', '_', f"selected_{'_'.join(selected_servers)}")
            display_comparison_matrix(vendors, matrix_key)
    
    # Tab 2: Dell Mapped Comparisons
    with tab2:
        st.markdown('<h2 class="sub-header">Dell Servers Mapped Comparisons</h2>', unsafe_allow_html=True)
        
        st.subheader("View Dell products with their mapped competitor equivalents")
        
        # Check if mapping data is available
        if mapping_df is None or len(mapping_df) == 0:
            st.warning("Server mapping data not available. Please ensure server_mapping table exists in the database.")
            return
        
        # Get Dell servers from master data
        dell_servers = master_df[master_df['Company'] == 'Dell']
        
        if len(dell_servers) == 0:
            st.warning("No Dell servers found in the database.")
        else:
            # Filter Dell servers to only include those with at least one valid competitor mapping
            dell_products_with_mappings = []
            
            for dell_product in dell_servers['Product Name'].unique():
                # Get mapping information for this Dell product
                mapping_info = mapping_df[mapping_df['Dell Server'] == dell_product]
                
                # If not found, try with normalized name
                if len(mapping_info) == 0:
                    normalized_dell_product = normalize_product_name_for_comparison(dell_product, 'Dell')
                    mapping_info = mapping_df[mapping_df['Dell Server'] == normalized_dell_product]
                
                # If not found, try with normalized name
                if len(mapping_info) == 0:
                    normalized_dell_product = normalize_product_name_for_comparison(dell_product, 'Dell')
                    mapping_info = mapping_df[mapping_df['Dell Server'] == normalized_dell_product]
                
                if len(mapping_info) > 0:
                    mapping_row = mapping_info.iloc[0]
                    lenovo_equivalent = mapping_row['Lenovo Server']
                    supermicro_equivalent = mapping_row['Supermicro Server']
                    
                    # Check if at least one valid mapping exists
                    has_valid_lenovo = (
                        pd.notna(lenovo_equivalent) and 
                        str(lenovo_equivalent).strip() != '' and 
                        str(lenovo_equivalent).upper() != 'TBD' and
                        str(lenovo_equivalent).strip() != 'No direct comparable yet'
                    )
                    has_valid_supermicro = (
                        pd.notna(supermicro_equivalent) and 
                        str(supermicro_equivalent).strip() != '' and 
                        str(supermicro_equivalent).upper() != 'TBD' and
                        str(supermicro_equivalent).strip() != 'No direct comparable yet'
                    )
                    
                    # Include if at least one valid mapping exists
                    if has_valid_lenovo or has_valid_supermicro:
                        dell_products_with_mappings.append(dell_product)
            
            # Filter by Dell product (only show products with valid mappings)
            if len(dell_products_with_mappings) == 0:
                st.warning("No Dell servers with valid competitor mappings found in the database.")
                return
            
            dell_products = ['All'] + sorted(dell_products_with_mappings)
            selected_dell_product = st.selectbox("Select Dell Product", dell_products)
            
            if selected_dell_product == 'All':
                st.info("Select a specific Dell product to view mapped comparisons.")
            else:
                # Get selected Dell server data
                dell_server_data = dell_servers[dell_servers['Product Name'] == selected_dell_product].iloc[0]
                
                # Get mapping information
                mapping_info = mapping_df[mapping_df['Dell Server'] == selected_dell_product]
                
                # Display side-by-side comparison
                st.markdown("### Side-by-Side Comparison")
                st.markdown(f"**{selected_dell_product}** vs Competitors")
                
                if len(mapping_info) == 0:
                    st.warning("No comparable system has been mapped for this Dell product.")
                else:
                    mapping_row = mapping_info.iloc[0]
                    
                    # Get competitor data - handle multiple competitors
                    lenovo_servers = []
                    supermicro_servers = []
                    
                    # Collect all Lenovo competitors
                    for i in range(1, 4):  # Check Lenovo Server, Lenovo Server 2, Lenovo Server 3
                        col_name = f'Lenovo Server' if i == 1 else f'Lenovo Server {i}'
                        if col_name in mapping_row.index and pd.notna(mapping_row[col_name]):
                            lenovo_server = mapping_row[col_name]
                            if lenovo_server != 'TBD' and lenovo_server != '' and lenovo_server != 'No direct comparable yet':
                                lenovo_servers.append(lenovo_server)
                    
                    # Collect all Supermicro competitors
                    for i in range(1, 4):  # Check Supermicro Server, Supermicro Server 2, Supermicro Server 3
                        col_name = f'Supermicro Server' if i == 1 else f'Supermicro Server {i}'
                        if col_name in mapping_row.index and pd.notna(mapping_row[col_name]):
                            supermicro_server = mapping_row[col_name]
                            if supermicro_server != 'TBD' and supermicro_server != '' and supermicro_server != 'No direct comparable yet':
                                supermicro_servers.append(supermicro_server)
                    
                    # Find Lenovo server data for each competitor
                    lenovo_rows = []
                    for lenovo_server in lenovo_servers:
                        lenovo_data = master_df[
                            (master_df['Company'] == 'Lenovo') & 
                            (master_df['Product Name'] == lenovo_server)
                        ]
                        if len(lenovo_data) > 0:
                            lenovo_rows.append(lenovo_data.iloc[0])
                        else:
                            # Create placeholder row for products not in catalog
                            lenovo_rows.append({
                                'Company': 'Lenovo',
                                'Product Name': lenovo_server,
                                'Server Type': 'N/A',
                                'CPU': 'N/A',
                                'GPU': 'N/A', 
                                'Memory': 'N/A',
                                'Storage Drive Type': 'N/A',
                                'Max Drive Configuration': 'N/A'
                            })
                    
                    # Find Supermicro server data for each competitor
                    supermicro_rows = []
                    for supermicro_server in supermicro_servers:
                        supermicro_data = master_df[
                            (master_df['Company'] == 'Supermicro') & 
                            (master_df['Product Name'].apply(normalize_supermicro_name) == supermicro_server)
                        ]
                        if len(supermicro_data) > 0:
                            supermicro_rows.append(supermicro_data.iloc[0])
                    
                    # Build vendor list dynamically based on available competitors
                    vendors = [
                        {'company': 'Dell', 'product': selected_dell_product, 'server_type': dell_server_data.get('Server Type', 'Unknown'), 'row': dell_server_data, 'color': '#0076CE', 'found': True}
                    ]
                    
                    # Add Lenovo competitors
                    for i, lenovo_row in enumerate(lenovo_rows):
                        if isinstance(lenovo_row, dict):
                            # Placeholder for product not in catalog
                            vendors.append({
                                'company': 'Lenovo',
                                'product': lenovo_row['Product Name'],
                                'server_type': 'N/A',
                                'row': lenovo_row,
                                'color': '#E2231A',
                                'found': False
                            })
                        else:
                            vendors.append({
                                'company': 'Lenovo',
                                'product': format_product_name_for_display(lenovo_row),
                                'server_type': lenovo_row.get('Server Type', 'Unknown'),
                                'row': lenovo_row,
                                'color': '#E2231A',
                                'found': True
                            })
                    
                    # Add Supermicro competitors if available
                    for i, supermicro_row in enumerate(supermicro_rows):
                        vendors.append({
                            'company': 'Supermicro',
                            'product': format_product_name_for_display(supermicro_row),
                            'server_type': supermicro_row.get('Server Type', 'Unknown'),
                            'row': supermicro_row,
                            'color': '#28A745',
                            'found': True
                        })
                    
                    matrix_key = re.sub(r'[^a-zA-Z0-9_]', '_', f"mapped_{selected_dell_product}")
                    display_comparison_matrix(vendors, matrix_key)

if __name__ == "__main__":
    main()
