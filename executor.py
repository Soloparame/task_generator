import subprocess
import os

def write_files(files, folder="tasks"):
    os.makedirs(folder, exist_ok=True)
    for filename, content in files.items():
        file_path = os.path.join(folder, filename)
        with open(file_path, "w") as f:
            f.write(content)
        print(f"✅ File written: {file_path}")

def run_commands(commands, folder="tasks"):
    for cmd in commands:
        cmd_lower = cmd.lower()
        
        # Skip invalid shell commands or descriptive lines
        if (
            not cmd.strip()
            or cmd.strip().endswith(":")
            or any(kw in cmd_lower for kw in ["touch", "echo", "create", "edit", "description", "open", "save"])
        ):
            print(f"⚠️ Skipping unsupported or descriptive command: {cmd}")
            continue

        try:
            print(f"🚀 Running: cd {folder} && {cmd}")
            subprocess.run(cmd, cwd=folder, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {cmd}")
            print(e)
            return False
    return True
