import os
import subprocess
import sys

# Change to the correct directory
os.chdir(r'C:\Users\Paula_Garzon\OneDrive - Dell Technologies\Desktop\Paula G\Cleaned Data\server-comparison-tool')

# Set environment variable to skip email prompt
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Run the app from the correct directory
result = subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])

print(f"App exited with code: {result.returncode}")
