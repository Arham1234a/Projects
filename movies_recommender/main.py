import subprocess

# Step 1 – run your first file
subprocess.run(["python", "projects-file.py"])

# Step 2 – now run streamlit app

subprocess.run(["streamlit", "run", "app.py"])