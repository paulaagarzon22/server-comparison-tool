import streamlit as st
import pandas as pd
import sqlite3
import json
import hashlib
from typing import List, Dict, Any

# Database configuration
DB_FILE = 'companies_data.db'

# Page configuration
st.set_page_config(
    page_title="Server Configuration Comparison Tool",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
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
        if len(value) == 1:
            return value[0]
        # Return as HTML list for proper styling
        list_items = [f"<li>{str(item)}</li>" for item in value]
        return f"<ul>{''.join(list_items)}</ul>"
    return str(value)

def display_list_with_show_more(value, key_prefix):
    """Display list with show more functionality using proper HTML list styling"""
    if value is None:
        st.write("N/A")
        return
    if not isinstance(value, list):
        st.write(str(value))
        return
    
    # Separate summary lines from configuration options
    summary_lines = []
    config_options = []
    
    for item in value:
        item_str = str(item).strip()
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
    
    if len(config_options) <= 5:
        # Show all items as a proper HTML list
        html_list = f"<ul>{''.join(list_items)}</ul>"
        st.markdown(html_list, unsafe_allow_html=True)
    else:
        show_more_key = f"show_more_{key_prefix}"
        
        # Initialize session state if not exists
        if show_more_key not in st.session_state:
            st.session_state[show_more_key] = False
        
        if st.session_state[show_more_key]:
            # Show all items as a proper HTML list
            html_list = f"<ul>{''.join(list_items)}</ul>"
            st.markdown(html_list, unsafe_allow_html=True)
            if st.button("Show less", key=f"less_{key_prefix}"):
                st.session_state[show_more_key] = False
                st.rerun()
        else:
            # Show first 5 items as a proper HTML list
            html_list = f"<ul>{''.join(list_items[:5])}</ul>"
            st.markdown(html_list, unsafe_allow_html=True)
            if st.button(f"Show more ({len(config_options) - 5} more)", key=f"more_{key_prefix}"):
                st.session_state[show_more_key] = True
                st.rerun()

def display_list_with_show_more_compact(value, key_prefix):
    """Display list with show more functionality in compact format for comparison columns"""
    if value is None:
        st.write("N/A")
        return
    if not isinstance(value, list):
        st.write(str(value))
        return
    
    # Separate summary lines from configuration options
    summary_lines = []
    config_options = []
    
    for item in value:
        item_str = str(item).strip()
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
        if len(config_options) <= 3:  # Show fewer items in compact view
            # Show all items as a proper HTML list
            list_items = [f"<li>{str(item)}</li>" for item in config_options]
            html_list = f"<ul style='margin: 0; padding-left: 20px; font-size: 12px;'>{''.join(list_items)}</ul>"
            st.markdown(html_list, unsafe_allow_html=True)
        else:
            show_more_key = f"show_more_{key_prefix}"
            
            # Initialize session state if not exists
            if show_more_key not in st.session_state:
                st.session_state[show_more_key] = False
            
            if st.session_state[show_more_key]:
                # Show all items as a proper HTML list
                list_items = [f"<li>{str(item)}</li>" for item in config_options]
                html_list = f"<ul style='margin: 0; padding-left: 20px; font-size: 12px;'>{''.join(list_items)}</ul>"
                st.markdown(html_list, unsafe_allow_html=True)
                if st.button("Show less", key=f"less_{key_prefix}"):
                    st.session_state[show_more_key] = False
                    st.rerun()
            else:
                # Show first 3 items as a proper HTML list
                list_items = [f"<li>{str(item)}</li>" for item in config_options[:3]]
                html_list = f"<ul style='margin: 0; padding-left: 20px; font-size: 12px;'>{''.join(list_items)}</ul>"
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
    if 'lenovo_configurations_' in table_name:
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
        st.markdown('<h1 class="main-header">🖥️ Server Configuration Comparison Tool</h1>', unsafe_allow_html=True)
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
    json_columns = ['CPU', 'GPU', 'Memory', 'Storage Drive Type', 'Max Drive Configuration', 'Storage Controller']
    for col in json_columns:
        if col in master_df.columns:
            master_df[col] = master_df[col].apply(parse_json_column)
    
    # Sidebar for filtering
    st.sidebar.header("🔍 Filters")
    
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
    tab1, tab2, tab3 = st.tabs(["📊 Catalog", "🔗 Dell Mapped Comparisons", "⚖️ User Selected Comparisons"])
    
    # Tab 1: Catalog View
    with tab1:
        st.markdown('<h2 class="sub-header">Server Catalog</h2>', unsafe_allow_html=True)
        
        # Add search bar
        search_term = st.text_input("🔍 Search servers", "", placeholder="Search by product name, company, server type, CPU, GPU, etc.")
        
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
            
            # Create comparison table
            comparison_df = pd.DataFrame(comparison_data)
            
            # Display comparison
            st.markdown("### Comparison Table")
            
            # Define columns to compare
            compare_columns = ['Company', 'Product Name', 'Server Type', 'CPU', 'GPU', 'Memory', 
                            'Storage Drive Type', 'Max Drive Configuration']
            
            # Create comparison display
            for col in compare_columns:
                if col in comparison_df.columns:
                    with st.container():
                        st.markdown(f"**{col.replace('_', ' ')}**")
                        cols = st.columns(len(selected_servers))
                        for idx, server_data in enumerate(comparison_data):
                            with cols[idx]:
                                display_list_with_show_more(server_data.get(col, 'N/A'), f"comp_{col}_{idx}")
                        st.markdown("---")
    
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
                    
                    # Get competitor data
                    lenovo_server = mapping_row['Lenovo Server']
                    supermicro_server = mapping_row['Supermicro Server']
                    
                    # Find Lenovo server data
                    lenovo_row = None
                    if pd.notna(lenovo_server) and lenovo_server != 'TBD' and lenovo_server != '':
                        lenovo_data = master_df[
                            (master_df['Company'] == 'Lenovo') & 
                            (master_df['Product Name'] == lenovo_server)
                        ]
                        if len(lenovo_data) > 0:
                            lenovo_row = lenovo_data.iloc[0]
                    
                    # Find Supermicro server data
                    supermicro_row = None
                    if pd.notna(supermicro_server) and supermicro_server != 'TBD' and supermicro_server != '':
                        supermicro_data = master_df[
                            (master_df['Company'] == 'Supermicro') & 
                            (master_df['Product Name'].apply(normalize_supermicro_name) == supermicro_server)
                        ]
                        if len(supermicro_data) > 0:
                            supermicro_row = supermicro_data.iloc[0]
                    
                    # Create 3-column comparison with visual dividers using markdown
                    col_dell, col_lenovo, col_supermicro = st.columns([1, 1, 1])
                    
                    # Dell column
                    with col_dell:
                        st.markdown(f"""
                        <div style='border-right: 2px solid #E0E0E0; padding-right: 15px;'>
                            <div style='border-left: 4px solid #0076CE; padding-left: 10px; margin-bottom: 15px;'>
                                <div style='font-size: 16px; font-weight: bold; color: #0076CE; margin-bottom: 5px;'>Dell</div>
                                <div style='font-size: 14px; font-weight: bold;'>{selected_dell_product}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("---")
                        display_server_details_compact(dell_server_data, "dell_compact")
                    
                    # Lenovo column
                    with col_lenovo:
                        if lenovo_row is not None:
                            st.markdown(f"""
                            <div style='border-right: 2px solid #E0E0E0; padding-right: 15px;'>
                                <div style='border-left: 4px solid #E2231A; padding-left: 10px; margin-bottom: 15px;'>
                                    <div style='font-size: 16px; font-weight: bold; color: #E2231A; margin-bottom: 5px;'>Lenovo</div>
                                    <div style='font-size: 14px; font-weight: bold;'>{lenovo_server}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown("---")
                            display_server_details_compact(lenovo_row, "lenovo_compact")
                        else:
                            st.markdown(f"""
                            <div style='border-right: 2px solid #E0E0E0; padding-right: 15px;'>
                                <div style='border-left: 4px solid #E2231A; padding-left: 10px; margin-bottom: 15px;'>
                                    <div style='font-size: 16px; font-weight: bold; color: #E2231A; margin-bottom: 5px;'>Lenovo</div>
                                    <div style='font-size: 12px; color: #666;'>No comparable system has been mapped</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Supermicro column
                    with col_supermicro:
                        if supermicro_row is not None:
                            st.markdown(f"""
                            <div style='padding-left: 10px;'>
                                <div style='border-left: 4px solid #28A745; padding-left: 10px; margin-bottom: 15px;'>
                                    <div style='font-size: 16px; font-weight: bold; color: #28A745; margin-bottom: 5px;'>Supermicro</div>
                                    <div style='font-size: 14px; font-weight: bold;'>{supermicro_server}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown("---")
                            display_server_details_compact(supermicro_row, "supermicro_compact")
                        else:
                            st.markdown(f"""
                            <div style='padding-left: 10px;'>
                                <div style='border-left: 4px solid #28A745; padding-left: 10px; margin-bottom: 15px;'>
                                    <div style='font-size: 16px; font-weight: bold; color: #28A745; margin-bottom: 5px;'>Supermicro</div>
                                    <div style='font-size: 12px; color: #666;'>No comparable system has been mapped</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"**👤 Logged in as:** {st.session_state['username']}")
    st.markdown("**💡 Tip:** Use the filters in the sidebar to narrow down the catalog, then switch to the Comparison tab to compare specific models.")
    st.markdown("**📊 Data Source:** companies_data.db - Last updated: Database file timestamp")
    
    # Credentials info (in a collapsible section)
    with st.expander("🔑 Login Credentials"):
        st.markdown("""
        **Default Login Credentials:**
        - Username: `admin` | Password: `admin123`
        - Username: `procurement` | Password: `procurement123`
        - Username: `dell` | Password: `dell123`
        
        **Note:** These are default credentials. In production, use a proper authentication system with secure password storage.
        """)

if __name__ == "__main__":
    main()
