import os

def execute_lines_from_file(filename):
    if not filename.endswith('.eaa'):
        print("Invalid file format. Please provide a .eaa file.")
        return

    if not os.path.exists(filename):
        print(f"File '{filename}' not found.")
        return

    with open(filename, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line:  # Skip empty lines
                print(f"Executing: {stripped_line}")
                os.system(stripped_line)

