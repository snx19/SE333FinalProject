# server.py
from fastmcp import FastMCP
import re
import subprocess
import os

import xml.etree.ElementTree as ET

mcp = FastMCP("Tester Agent")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def generate_tests(java_file_path: str) -> str:
    """Generate JUnit tests based on signature methods"""

    if not os.path.exists(java_file_path):
        return "Error: file not found."

    try:
        code = open(java_file_path, 'r').read()
    except Exception as e:
        return f"Error: file {e}"
    
    # finds method names
    methods = re.findall(
        r'public\s+(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\(', code)
    
    if not methods:
        return f"No public methods found in {java_file_path}."

    # JUnit test class
    classname = os.path.splitext(os.path.basename(java_file_path))[0]
    test_class_name = f"{classname}Test"

    test_code = "import org.junit.Test;\nimport static org.junit.Assert.*;\n\n"
    test_code += f"public class {test_class_name} {{\n"

    for m in methods:
        if m == classname:
            continue  # skip constructor
        test_code += f"    @Test\n public void test{m}() {{\n"
        test_code += f"        // TODO: implement test for {m}\n"
        test_code += f"    }}\n\n"

    test_code += "}\n"

    # output
    output_path = os.path.join(os.path.dirname(java_file_path), f"{test_class_name}.java")
    try:
        with open(output_path, "w") as f:
            f.write(test_code)
    except Exception as e:
        return f"Error writing test file: {e}"
    
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

def automated_tests(iterations: int = 3) -> str:
    """Automated testing and code improvement"""
    log = []
    for i in range(iterations):
        log.append(f"--- Iteration {i+1} ---")

        # 1. run tests
        run_output = run_tests()
        log.append("Test run output:\n" + run_output)

        # 2. analyze coverage
        coverage_file = "target/site/jacoco/jacoco.xml"
        uncovered = coverage_analysis(coverage_file)
        log.append("Coverage analysis:\n" + uncovered)

        # 3. identify failing tests
        failing_tests = [
            line.split()[1]
            for line in run_output.splitlines()
            if "FAILURE!" in line or "Exception" in line
        ]

        # 4. fix bugs for failing tests
        for failing_test in failing_tests:
            # map test class name to source file
            class_name = failing_test.replace("Test", "")
            # search in src/main/java
            src_file = None
            for root, dirs, files in os.walk("src/main/java/"):
                for file in files:
                    if file == f"{class_name}.java":
                        src_file = os.path.join(root, file)
                        break
                if src_file:
                    break
            if src_file:
                fix_result = fix_bug(src_file, failing_test)
                log.append(fix_result)
            else:
                log.append(f"Could not find source file for failing test: {failing_test}")
        
        # 5. generate tests
        for method in uncovered.splitlines():
            generate_tests("src/main/java/")
            log.append(f"Generated tests for method: {method}")

        # 6. stage, commit, and push changes
        git_add_all()
        git_commit(f"Automated tests iteration {i+1}")
        git_push()
        log.append(f"Pushed changes to remote.")

        # 7. stops if covered
        if uncovered.strip() == "All covered":
            log.append("All code covered. Stopping.")
            break

    return "\n".join(log)

@mcp.tool
def fix_bug(file_path: str, failing_test: str) -> str:
    """Automatically try to fix a bug based on a failing test"""
    
    if not os.path.exists(file_path):
        return f"Error: file not found: {file_path}"
    
    try:
        original = open(file_path, 'r').read()
    except Exception as e:
        return f"Error reading file: {e}"
    
    prompt = f"""
The following Java file has a bug that causes the test '{failing_test}' to fail.

Failing test:
{failing_test}

File contents:
------------------
{original}
------------------

Fix the bug and return only the corrected java file contents.
"""
    # use model to write fixed code
    fixed_code = mcp.run_model(prompt)
    # fixed version
    try:
        with open(file_path, "w") as f:
            f.write(fixed_code)
    except Exception as e:
        return f"Error writing fixed file: {e}"
    return f"bug fixed in {file_path}"
            

if __name__ == "__main__":
    mcp.run(transport="sse")

# source .venv/bin/activate
# python server.py