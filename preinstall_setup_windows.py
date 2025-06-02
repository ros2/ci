"""
Name: preinstall_setup_windows.py

Purpose: 
A python script to update shebang lines in Python files to the current Python executable in a Pixi Pixi environment and directory. 

Instructions:
1. Place this file inside the zipped release ROS 2 distro
2. Navigate to inside the ROS 2 binary folder
3. In a command prompt, activate your Pixi (Conda) environment
4. Run: python preinstall_setup_windows.py and wait until the script is done

Author: Kimberly McGuire (Independent)*
* co-authored with Github Copilot
"""

import os
import sys
import shutil

def update_shebangs(folder, new_shebang):
    """Replace shebang lines in all .py files under folder with a progress bar, excluding anything in .pixi folders."""
    py_files = []
    for root, _, files in os.walk(folder):
        # Skip any directory that contains '.pixi' in its path
        if '.pixi' in os.path.relpath(root, folder).split(os.sep):
            continue
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))

    # TODO: The 'rqt_bag' file (no extension) also needs its shebang replaced.
    # This is currently not handled by this script. Consider adding logic to find and patch it.

    total = len(py_files)
    if total == 0:
        print("No Python files found.")
        return

    def print_progress(idx, total, bar_len=40):
        filled = int(bar_len * idx / total)
        bar = '=' * filled + '-' * (bar_len - filled)
        print(f"\rProcessing: [{bar}] {idx}/{total}", end='', flush=True)

    for idx, file_path in enumerate(py_files, 1):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Only replace if the first line is a shebang
        if lines and lines[0].startswith('#!'):
            lines[0] = new_shebang + '\n'
            tmp_path = file_path + '.tmp'
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            shutil.move(tmp_path, file_path)
        print_progress(idx, total)
    print()  # Move to next line after progress bar

def update_colcon_python_executable_in_setup_files(folder, python_path):
    """
    Update the hardcoded Python path in local_setup.ps1 and local_setup.bat to the given python_path.
    """
    ps1_path = os.path.join(folder, "local_setup.ps1")
    bat_path = os.path.join(folder, "local_setup.bat")

    # Update local_setup.ps1
    if os.path.exists(ps1_path):
        with open(ps1_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith('$_colcon_python_executable=') and 'pixi_ws' in line:
                # Replace the assignment line
                new_lines.append(f'  $_colcon_python_executable="{python_path}"\n')
            else:
                new_lines.append(line)
        with open(ps1_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"Updated Python path in {ps1_path}")

    # Update local_setup.bat
    if os.path.exists(bat_path):
        with open(bat_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith('set "_colcon_python_executable=') and 'pixi_ws' in line:
                new_lines.append(f'    set "_colcon_python_executable={python_path}"\n')
            else:
                new_lines.append(line)
        with open(bat_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"Updated Python path in {bat_path}")

def main():
    # Check for Pixi/Conda environment
    if "CONDA_PREFIX" not in os.environ:
        print("Error: This script must be run inside a Pixi (Conda) environment.")
        sys.exit(1)

    folder = os.path.dirname(os.path.abspath(__file__))
    python_path = sys.executable  # Use the current environment's Python
    new_shebang = f'#!{python_path}'
    print(f"Using Python executable: {python_path}")
    update_shebangs(folder, new_shebang)
    update_colcon_python_executable_in_setup_files(folder, python_path)
    print("Done!")

if __name__ == "__main__":
    main()