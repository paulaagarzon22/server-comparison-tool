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
    except Exception as e:
        st.error(f"Error loading database: {e}")
        st.info("Please ensure 'companies_data.db' is in the same directory as this app.")
        return
    
    # Combine all data into a single DataFrame with company and server type info
    combined_data = []
    for table_name, df in all_data.items():
        df_copy = df.copy()
        df_copy['Company'] = get_company_from_table(table_name)
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
    tab1, tab2, tab3 = st.tabs(["📊 Catalog", "⚖️ Comparison", "📈 Gap Analysis"])
    
    # Tab 1: Catalog View
    with tab1:
        st.markdown('<h2 class="sub-header">Server Catalog</h2>', unsafe_allow_html=True)
        
        if len(filtered_df) == 0:
            st.warning("No servers found matching the selected filters.")
        else:
            st.info(f"Showing {len(filtered_df)} server(s)")
            
            # Display servers as cards
            for idx, row in filtered_df.iterrows():
                with st.expander(f"{row['Company']} - {row['Product Name']} ({row['Server Type']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Basic Information**")
                        st.write(f"**Company:** {row['Company']}")
                        st.write(f"**Product:** {row['Product Name']}")
                        st.write(f"**Server Type:** {row['Server Type']}")
                    
                    with col2:
                        st.markdown("**Specifications**")
                        st.write(f"**CPU:** {format_display_value(row.get('CPU', 'N/A'))}")
                        st.write(f"**GPU:** {format_display_value(row.get('GPU', 'N/A'))}")
                        st.write(f"**Memory:** {format_display_value(row.get('Memory', 'N/A'))}")
                    
                    st.markdown("**Storage Information**")
                    col3, col4 = st.columns(2)
                    with col3:
                        st.write(f"**Drive Type:** {format_display_value(row.get('Storage Drive Type', 'N/A'))}")
                    with col4:
                        st.write(f"**Max Configuration:** {format_display_value(row.get('Max Drive Configuration', 'N/A'))}")
                    
                    if pd.notna(row.get('Storage Controller')):
                        st.write(f"**Storage Controller:** {format_display_value(row['Storage Controller'])}")
    
    # Tab 2: Side-by-Side Comparison
    with tab2:
        st.markdown('<h2 class="sub-header">Side-by-Side Comparison</h2>', unsafe_allow_html=True)
        
        # Server selection for comparison
        st.subheader("Select Servers to Compare")
        
        # Get available servers for selection
        available_servers = filtered_df[['Company', 'Product Name', 'Server Type']].copy()
        available_servers['Display Name'] = available_servers['Company'] + ' - ' + available_servers['Product Name']
        
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
                            'Storage Drive Type', 'Max Drive Configuration', 'Storage Controller']
            
            # Create comparison display
            for col in compare_columns:
                if col in comparison_df.columns:
                    with st.container():
                        st.markdown(f"**{col.replace('_', ' ')}**")
                        cols = st.columns(len(selected_servers))
                        for idx, server_data in enumerate(comparison_data):
                            with cols[idx]:
                                st.write(format_display_value(server_data.get(col, 'N/A')))
                        st.markdown("---")
    
    # Tab 3: Gap Analysis
    with tab3:
        st.markdown('<h2 class="sub-header">Gap Analysis</h2>', unsafe_allow_html=True)
        
        st.subheader("Dell vs Competitors Analysis")
        
        # Get Dell servers and competitor servers
        dell_servers = master_df[master_df['Company'] == 'Dell']
        competitor_servers = master_df[master_df['Company'] != 'Dell']
        
        if len(dell_servers) == 0:
            st.warning("No Dell servers found in the database.")
        elif len(competitor_servers) == 0:
            st.warning("No competitor servers found in the database.")
        else:
            st.info(f"Analyzing {len(dell_servers)} Dell servers vs {len(competitor_servers)} competitor servers")
            
            # Overall statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Dell Server Models", len(dell_servers))
            with col2:
                st.metric("Competitor Models", len(competitor_servers))
            with col3:
                st.metric("Total Companies", master_df['Company'].nunique())
            
            st.markdown("---")
            
            # Server type comparison
            st.subheader("Server Type Coverage")
            
            dell_server_types = set(dell_servers['Server Type'].unique())
            competitor_server_types = set(competitor_servers['Server Type'].unique())
            
            # Server types Dell has that competitors don't
            dell_exclusive = dell_server_types - competitor_server_types
            # Server types competitors have that Dell doesn't
            competitor_exclusive = competitor_server_types - dell_server_types
            # Server types both have
            common_types = dell_server_types & competitor_server_types
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Dell Exclusive Server Types**")
                if dell_exclusive:
                    for server_type in sorted(dell_exclusive):
                        st.write(f"• {server_type}")
                else:
                    st.write("None")
            
            with col2:
                st.markdown("**Common Server Types**")
                if common_types:
                    for server_type in sorted(common_types):
                        st.write(f"• {server_type}")
                else:
                    st.write("None")
            
            with col3:
                st.markdown("**Competitor Exclusive Server Types**")
                if competitor_exclusive:
                    for server_type in sorted(competitor_exclusive):
                        st.write(f"• {server_type}")
                else:
                    st.write("None")
            
            st.markdown("---")
            
            # Company breakdown
            st.subheader("Market Coverage by Company")
            
            company_stats = master_df.groupby('Company').agg({
                'Product Name': 'count',
                'Server Type': 'nunique'
            }).rename(columns={'Product Name': 'Total Models', 'Server Type': 'Server Types'})
            
            st.dataframe(company_stats, use_container_width=True)
            
            # Detailed gap analysis by server type
            st.markdown("---")
            st.subheader("Detailed Analysis by Server Type")
            
            selected_analysis_type = st.selectbox(
                "Select Server Type for Detailed Analysis",
                sorted(master_df['Server Type'].unique())
            )
            
            if selected_analysis_type:
                type_dell = dell_servers[dell_servers['Server Type'] == selected_analysis_type]
                type_competitors = competitor_servers[competitor_servers['Server Type'] == selected_analysis_type]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Dell {selected_analysis_type}**")
                    if len(type_dell) > 0:
                        st.write(f"Models: {len(type_dell)}")
                        for idx, row in type_dell.head(5).iterrows():
                            st.write(f"• {row['Product Name']}")
                        if len(type_dell) > 5:
                            st.write(f"... and {len(type_dell) - 5} more")
                    else:
                        st.write("No Dell models in this category")
                
                with col2:
                    st.markdown(f"**Competitor {selected_analysis_type}**")
                    if len(type_competitors) > 0:
                        st.write(f"Models: {len(type_competitors)}")
                        for idx, row in type_competitors.head(5).iterrows():
                            company = row['Company']
                            st.write(f"• {company}: {row['Product Name']}")
                        if len(type_competitors) > 5:
                            st.write(f"... and {len(type_competitors) - 5} more")
                    else:
                        st.write("No competitor models in this category")

if __name__ == "__main__":
    main()
