import subprocess
import os
import re
import platform
from ai_utils import get_plan_from_ai

def write_files(files, folder="tasks"):
    """Write files to the specified folder."""
    if not os.path.exists(folder):
        os.makedirs(folder)
    for filename, content in files.items():
        filepath = os.path.join(folder, filename)
        # Clean the content to remove markdown and any unwanted syntax
        cleaned_content = clean_code(content)
        with open(filepath, "w") as f:
            f.write(cleaned_content)
        print(f"✅ File written: {filepath}")

def clean_code(content):
    """Remove any unwanted markdown or syntax from the generated code."""
    # Removing code block syntax like ```python and ```
    content = re.sub(r"```python|```", "", content)
    return content.strip()

# Ensure tasks folder exists
TASKS_FOLDER = "tasks"
if not os.path.exists(TASKS_FOLDER):
    os.makedirs(TASKS_FOLDER)

def parse_ai_response(response):
    """Parse the AI response into plan, commands, and files."""
    plan = re.search(r"PLAN:(.*?)COMMANDS:", response, re.DOTALL).group(1).strip()
    cmds = re.search(r"COMMANDS:(.*?)FILES:", response, re.DOTALL).group(1).strip().splitlines()
    files_raw = response.split("FILES:")[1].strip()

    files = {}
    file_blocks = files_raw.split("---")
    for block in file_blocks:
        lines = block.strip().split("\n")
        if not lines or ":" not in lines[0]:
            continue
        file_name = lines[0].split(":")[0].strip("- ").strip()
        content = "\n".join(lines[1:])
        files[file_name] = content
    return plan, cmds, files

def clean_commands(commands):
    """Clean commands by removing numbering and adjusting for the OS."""
    cleaned_commands = []
    for command in commands:
        # Remove leading numbering like "1.", "2."
        cleaned_command = re.sub(r"^\d+\.\s*", "", command.strip())

        # OS-specific command adjustments
        if platform.system() == "Windows":
            cleaned_command = cleaned_command.replace("touch", "echo. >")

        cleaned_commands.append(cleaned_command)
    return cleaned_commands

def execute_commands(commands, task_folder, files):
    """Execute commands and automatically run Python scripts."""
    # Skip creation commands like 'touch' since the file is already written
    print("🚀 Skipping file creation commands as files are already written.")

    # Automatically execute Python scripts in the tasks folder
    for file_name in files.keys():
        if file_name.endswith(".py"):
            python_command = f"python {os.path.join(task_folder, file_name)}"
            print(f"🚀 Running Python script: {python_command}")
            result = subprocess.run(python_command, shell=True)
            if result.returncode != 0:
                print(f"❌ Python script failed: {python_command}")
                return False

    return True
def add_default_inputs_to_script(command, folder):
    """Modify the Python script to include default inputs."""
    script_name = command.split("python")[-1].strip()
    script_path = os.path.join(folder, script_name)

    # Check if the script uses input()
    with open(script_path, "r") as f:
        code = f.read()

    if "input(" in code:
        print("🔧 Modifying script to replace inputs with defaults...")
        # Replace input() with default values
        code = re.sub(r"input\((.*?)\)", "'42'", code)  # Example: Replace with '42'

        # Write the modified script back
        with open(script_path, "w") as f:
            f.write(code)

    return command

def main():
    """Main function to handle AI task execution."""
    print("🎯 AI Task Agent")
    task = input("What task would you like me to do?\n> ")

    while True:
        # Get response from AI (plan, commands, and files)
        response = get_plan_from_ai(task)
        plan, commands, files = parse_ai_response(response)

        print("\n📝 Plan:\n", plan)
        print("\n📂 Commands to run:\n", "\n".join(commands))
        print("\n📄 Files to be created:")
        for f in files:
            print(f" - {f}")

        approve = input("\n✅ Proceed with these actions? (y/n): ")
        if approve.lower() != 'y':
            print("❌ Task aborted.")
            return

        # Write the files to the tasks folder
        write_files(files, TASKS_FOLDER)

        # Clean the commands to remove numbers like "1.", "2."
        cleaned_commands = clean_commands(commands)

        # Run the cleaned commands in the tasks folder
        if not execute_commands(cleaned_commands, TASKS_FOLDER, files):
            print("❌ There was an error while executing the commands.")
            reason = input("❓ What went wrong? ")
            task = f"{task}. The problem was: {reason}. Fix and retry."
            continue

        # Check if task was successful
        success = input("\n✅ Was the task successful? (y/n): ")
        if success.lower() == 'y':
            print("🎉 Task complete.")
            break
        else:
            reason = input("❓ What went wrong? ")
            task = f"{task}. The problem was: {reason}. Fix and retry."

if __name__ == "__main__":
    main()