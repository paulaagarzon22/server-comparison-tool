# Server Configuration Comparison Tool

A web-based tool for comparing server configurations across Dell, Lenovo, and Supermicro products.

## Features

- **📊 Catalog View**: Browse server configurations by company and type
- **⚖️ Side-by-Side Comparison**: Compare up to 4 servers simultaneously
- **📈 Gap Analysis**: Analyze Dell vs competitor market positioning
- **🔐 Authentication**: Simple login system for team access

## Data Source

This application reads from `companies_data.db` SQLite database containing:
- Dell server configurations (50 models)
- Lenovo server configurations (26 models)
- Supermicro server configurations (59 models across 4 categories)

## Login Credentials

- Username: `admin` | Password: `admin123`
- Username: `procurement` | Password: `procurement123`
- Username: `dell` | Password: `dell123`

## Deployment

This app is deployed on Streamlit Cloud.

## Data Updates

To update the data:
1. Modify the Excel source files
2. Run the import scripts to update `companies_data.db`
3. Deploy the updated database to Streamlit Cloud

## Technologies

- **Backend**: Streamlit (Python)
- **Database**: SQLite
- **Data Processing**: Pandas
