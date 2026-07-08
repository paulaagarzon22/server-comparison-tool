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
        if len(value) == 1:
            return value[0]
        return "• " + "\n• ".join(str(item) for item in value)
    return str(value)

def display_list_with_show_more(value, key_prefix):
    """Display list with show more functionality"""
    if value is None:
        st.write("N/A")
        return
    if not isinstance(value, list):
        st.write(str(value))
        return
    
    if len(value) <= 5:
        st.write("• " + "\n• ".join(str(item) for item in value))
    else:
        show_more_key = f"show_more_{key_prefix}"
        
        # Initialize session state if not exists
        if show_more_key not in st.session_state:
            st.session_state[show_more_key] = False
        
        if st.session_state[show_more_key]:
            # Show all items
            st.write("• " + "\n• ".join(str(item) for item in value))
            if st.button("Show less", key=f"less_{key_prefix}"):
                st.session_state[show_more_key] = False
                st.rerun()
        else:
            # Show first 5 items
            st.write("• " + "\n• ".join(str(item) for item in value[:5]))
            if st.button(f"Show more ({len(value) - 5} more)", key=f"more_{key_prefix}"):
                st.session_state[show_more_key] = True
                st.rerun()

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
        df_copy = df.copy()
        df_copy['Company'] = get_company_from_table(table_name)
        
        # For Dell servers, use mapping data for server type
        if df_copy['Company'].iloc[0] == 'Dell':
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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Catalog", "⚖️ Comparison", "📈 Gap Analysis", "🔗 Dell Mapped Comparisons"])
    
    # Tab 1: Catalog View
    with tab1:
        st.markdown('<h2 class="sub-header">Server Catalog</h2>', unsafe_allow_html=True)
        
        if len(filtered_df) == 0:
            st.warning("No servers found matching the selected filters.")
        else:
            st.info(f"Showing {len(filtered_df)} server(s)")
            
            # Display servers as cards
            for idx, row in filtered_df.iterrows():
                server_type = row.get('Server Type', 'Unknown')
                with st.expander(f"{row['Company']} - {row['Product Name']} ({server_type})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Basic Information**")
                        st.write(f"**Company:** {row['Company']}")
                        st.write(f"**Product:** {row['Product Name']}")
                        st.write(f"**Server Type:** {server_type}")
                    
                    with col2:
                        st.markdown("**Specifications**")
                        st.write(f"**CPU:**")
                        display_list_with_show_more(row.get('CPU', 'N/A'), f"cpu_{idx}")
                        st.write(f"**GPU:**")
                        display_list_with_show_more(row.get('GPU', 'N/A'), f"gpu_{idx}")
                        st.write(f"**Memory:**")
                        display_list_with_show_more(row.get('Memory', 'N/A'), f"memory_{idx}")
                    
                    st.markdown("**Storage Information**")
                    col3, col4 = st.columns(2)
                    with col3:
                        st.write(f"**Drive Type:**")
                        display_list_with_show_more(row.get('Storage Drive Type', 'N/A'), f"drive_{idx}")
                    with col4:
                        st.write(f"**Max Configuration:**")
                        display_list_with_show_more(row.get('Max Drive Configuration', 'N/A'), f"config_{idx}")
                    
                    if pd.notna(row.get('Storage Controller')):
                        st.write(f"**Storage Controller:**")
                        display_list_with_show_more(row['Storage Controller'], f"controller_{idx}")
    
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
                                display_list_with_show_more(server_data.get(col, 'N/A'), f"comp_{col}_{idx}")
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
            
            # Get Dell server types from mapping data
            if mapping_df is not None and len(mapping_df) > 0:
                dell_server_types = set(mapping_df['Server Category'].unique())
            else:
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
    
    # Tab 4: Dell Mapped Comparisons
    with tab4:
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
            # Filter by Dell product
            dell_products = ['All'] + sorted(dell_servers['Product Name'].unique().tolist())
            selected_dell_product = st.selectbox("Select Dell Product", dell_products)
            
            if selected_dell_product == 'All':
                st.info("Select a specific Dell product to view mapped comparisons.")
            else:
                # Get selected Dell server data
                dell_server_data = dell_servers[dell_servers['Product Name'] == selected_dell_product].iloc[0]
                
                # Get mapping information
                mapping_info = mapping_df[mapping_df['Dell Server'] == selected_dell_product]
                
                # Display Dell server info
                st.markdown("### Dell Server Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Product:** {dell_server_data['Product Name']}")
                    st.write(f"**Server Type:** {dell_server_data['Server Type']}")
                with col2:
                    st.write(f"**CPU:**")
                    display_list_with_show_more(dell_server_data.get('CPU', 'N/A'), f"dell_cpu")
                    st.write(f"**Memory:**")
                    display_list_with_show_more(dell_server_data.get('Memory', 'N/A'), f"dell_memory")
                
                st.markdown("---")
                
                # Display mapped comparisons
                st.markdown("### Mapped Competitor Comparisons")
                
                if len(mapping_info) == 0:
                    st.warning("No comparable system has been mapped for this Dell product.")
                else:
                    mapping_row = mapping_info.iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    # Lenovo comparison
                    with col1:
                        st.markdown("**Lenovo Equivalent**")
                        lenovo_server = mapping_row['Lenovo Server']
                        if pd.isna(lenovo_server) or lenovo_server == 'TBD' or lenovo_server == '':
                            st.write("No comparable system has been mapped")
                        else:
                            # Find Lenovo server data
                            lenovo_data = master_df[
                                (master_df['Company'] == 'Lenovo') & 
                                (master_df['Product Name'] == lenovo_server)
                            ]
                            if len(lenovo_data) > 0:
                                lenovo_row = lenovo_data.iloc[0]
                                st.write(f"**Product:** {lenovo_row['Product Name']}")
                                st.write(f"**Server Type:** {lenovo_row['Server Type']}")
                                st.write(f"**CPU:**")
                                display_list_with_show_more(lenovo_row.get('CPU', 'N/A'), f"lenovo_cpu")
                                st.write(f"**Memory:**")
                                display_list_with_show_more(lenovo_row.get('Memory', 'N/A'), f"lenovo_memory")
                            else:
                                st.write(f"Product '{lenovo_server}' not found in database")
                    
                    # Supermicro comparison
                    with col2:
                        st.markdown("**Supermicro Equivalent**")
                        supermicro_server = mapping_row['Supermicro Server']
                        if pd.isna(supermicro_server) or supermicro_server == 'TBD' or supermicro_server == '':
                            st.write("No comparable system has been mapped")
                        else:
                            # Find Supermicro server data
                            supermicro_data = master_df[
                                (master_df['Company'] == 'Supermicro') & 
                                (master_df['Product Name'] == supermicro_server)
                            ]
                            if len(supermicro_data) > 0:
                                supermicro_row = supermicro_data.iloc[0]
                                st.write(f"**Product:** {supermicro_row['Product Name']}")
                                st.write(f"**Server Type:** {supermicro_row['Server Type']}")
                                st.write(f"**CPU:**")
                                display_list_with_show_more(supermicro_row.get('CPU', 'N/A'), f"supermicro_cpu")
                                st.write(f"**Memory:**")
                                display_list_with_show_more(supermicro_row.get('Memory', 'N/A'), f"supermicro_memory")
                            else:
                                st.write(f"Product '{supermicro_server}' not found in database")
    
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
