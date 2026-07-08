import os
import subprocess
import sys

# Set environment variable to skip email prompt
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Run the app
result = subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'], 
                       cwd=r'C:\Users\Paula_Garzon\OneDrive - Dell Technologies\Desktop\Paula G\Cleaned Data\server-comparison-tool')

print(f"App exited with code: {result.returncode}")
