import sys
import os

# Set environment variable to skip email prompt
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Import and run the app
import streamlit
from app import main

if __name__ == "__main__":
    main()
