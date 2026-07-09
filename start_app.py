import os
import subprocess
import sys

# Change to the correct directory
os.chdir(r'C:\Users\Paula_Garzon\OneDrive - Dell Technologies\Desktop\Paula G\Cleaned Data\server-comparison-tool')

# Set environment variables
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_PORT'] = '8503'

# Run the app
print("Starting Server Configuration Comparison Tool...")
print("Access the app at: http://localhost:8503")
print("Press Ctrl+C to stop the app")

result = subprocess.run([
    sys.executable, 
    '-m', 
    'streamlit', 
    'run', 
    'app.py',
    '--server.port', '8503',
    '--server.headless', 'true'
])

print(f"App stopped with code: {result.returncode}")
