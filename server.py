# server.py
from fastmcp import FastMCP
import re
import subprocess

import xml.etree.ElementTree as ET

mcp = FastMCP("Tester Agent")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def generate_tests(java_file_path: str) -> str:
    """Generate JUnit tests based on signature methods"""
    try:
        code = open(java_file_path, 'r').read()
    except:
        return "Error: file not found."
    
    # finds method names
    methods = re.findall(r'public\s+\w+\s+(\w+)\s*\(', code)

    # JUnit test class
    test_code = "import org.junit.Test;\npublic class GeneratedTests {\n"
    for m in methods:
        test_code += f"\n @Test public void test{m}() {{}}\n"
    test_code += "}\n"

    # output
    with open("GeneratedTests.java", "w") as f:
        f.write(test_code)
    return f"Generated {len(methods)} tests in GeneratedTests.java"

@mcp.tool
def run_tests() -> str:
    """Run tests"""
    try:
        
        result = subprocess.run(
            ["mvn", "test"],
            capture_output=True,
            text=True,
        )
        return result.stdout
    except Exception as e:
        return f"Error running tests: {e}"
    
@mcp.tool
def coverage_analysis(xml_path: str) -> str:
    """Analyze code coverage from XML report"""
    

    try:
        tree = ET.parse(xml_path)
    except:
        return "Error: XML file not found or invalid."

    root = tree.getroot()

    uncovered = [
        m.attrib["name"]
        for m in root.findall(".//method")
        if int(m.attrib.get("missed", 0)) > 0
    ]
    return f"All covered" if not uncovered else "\n".join(uncovered)

@mcp.tool
def git_status() -> str:
    """Get git status"""
    try:
        # short status
        status = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
        ).stdout.strip()

        # check for conflicts
        conflicts = subprocess.run(
            ["git", "ls-files", "-u"],
            capture_output=True,
            text=True,
        ).stdout.strip()

        if not status and not conflicts:
            return "Clean"
        
        output = []

        if conflicts:
            output.append("Conflicts detected")

        if status:
            output.append("Changes:\n" + status)

        return "\n".join(output)
    
    except Exception as e:
        return f"Error: {e}"
    
@mcp.tool
def git_add_all() -> str:
    """Git add all changes"""
    try:
        # exclude directories
        ignore = ["target/" , "bin/", "build/", ".idea/", ".vscode/"]

        # get list of changed/untracked files
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
        ).stdout.splitlines()

        to_add = []
        for line in result:
            # remove status
            filepath = line[3:].strip()
            # skip ignored paths
            if any(filepath.startswith(ig) for ig in ignore):
                continue
            to_add.append(filepath)

        if not to_add:
            return "Nothing to stage."
            
        # stage files
        subprocess.run(["git", "add"] + to_add)

        return f"Staged {len(to_add)} files."
    
    except Exception as e:
        return f"Error: {e}"
    
@mcp.tool
def git_commit(message: str) -> str:
    """Git commit staged changes"""

    coverage = "unknown"
    try:
        tree = ET.parse("target/site/jacoco/jacoco.xml")
        root = tree.getroot()
        counter = root.find(".//counter[@type='INSTRUCTION']")
        missed = int(counter.attrib["missed"])
        covered = int(counter.attrib["covered"])
        coverage = f"{round((covered / (missed + covered)) * 100, 2)}%"
    except:
        coverage = "No coverage report found"

    # commit message
    commit_message = f"{message}\n\nCoverage: {coverage}"

    # run git commit
    result = subprocess.run(
        ["git", "commit", "-m", commit_message], 
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return result.stderr.strip()
    return f"Committed with coverage: {coverage}"

@mcp.tool
def git_push(remote: str = "origin") -> str:
    """Git push to remote"""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
        ).stdout.strip()

        if not branch:
            return "Could not determine current branch."
        
        # push with upstream
        result = subprocess.run(
            ["git", "push", "-u", remote, branch],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return result.stderr.strip()
        return f"Pushed branch '{branch}' to remote '{remote}'."

    except Exception as e:
        return f"Error: {e}"
    
@mcp.tool
def git_pull_request(
    title: str,
    body: str = "",
    base: str = "main",
) -> str:
    """Create a git pull request"""
    try:
        # create pull request
        result = subprocess.run(
            ["gh", "pr", "create", "--base", base, "--title", title, "--body", body],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return f"Error creating pull request: {result.stderr.strip()}"
        
        # github prints url of created pull request
        return result.stdout.strip()

    except Exception as e:
        return f"Error: {e}"




if __name__ == "__main__":
    mcp.run(transport="sse")


# source .venv/bin/activate
# python server.py