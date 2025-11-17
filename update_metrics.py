import subprocess
import os

java_files = sum(1 for root, dirs, files in os.walk(".") 
                 for file in files if file.endswith(".java"))

with open("metrics.txt", "w") as f:
    f.write(f"java_files: {java_files}\n")

print(f"Java files: {java_files}")

subprocess.run(["git", "add", "metrics.txt"])
# commits only if there are changes
subprocess.run(["git", "commit", "-m", "Update metrics"], check=False)
subprocess.run(["git", "push"], check=False)