# SE333FinalProject

# Instructions

# Install uv package manager
# Set up python virtual environment with MCP dependencies
# Configure VS code with MCP server integration

# Setup commands
uv init
uv venv

# Activate virtual environment using:

# On mac
source .venv/bin/activate 
uv add mcp[cli] httpx fastmcp

# On windows
venv\Scripts\activate
uv add mcp[cli] httpx fastmcp

# Run server
python server.py

# Tools
# Generate test for java files
/tester.generate_tests java_file_path="codebase/src/main/java"

# Run tests
/tester.run_tests

# Analyze coverage
/tester.coverage_analysis xml_path="codebase/target/site/jacoco/jacoco.xml"

# Stages changes
/tester.git_add_all

# Commits changes
/tester.git_commit message="Automated test generation"

# Push to origin
/tester.git_push remote="origin"

# Runs automated testing, including bug fixes improvements
/tester.automated_tests iterations=3