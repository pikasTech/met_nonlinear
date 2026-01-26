import os

# Define the content for each file
file_contents = {
    'utilities.py': [],
    'system.py': [],
    'curcuit_parameter.py': [],
    'met_parameter.py': [],
    'feedback_parameter.py': [],
    'c_fun.py': [],
    'met_data.py': [],
    'main.py': [],
}

# Define the mapping between class or function names and the corresponding files
mapping = {
    'formater': 'utilities.py',
    'stringfy': 'utilities.py',
    'getname': 'utilities.py',
    'System': 'system.py',
    'CurcuitParameter': 'curcuit_parameter.py',
    'METParameter': 'met_parameter.py',
    'FeedbackParameter': 'feedback_parameter.py',
    'CFun': 'c_fun.py',
    'METData': 'met_data.py',
    'loadData': 'main.py',
}

def main():
    # Read the contents of met.py
    with open('met.py', 'r') as f:
        lines = f.readlines()

    current_file = None
    for line in lines:
        # Check for class or function definitions
        for name, filename in mapping.items():
            if line.startswith(f'class {name}') or line.startswith(f'def {name}'):
                current_file = filename
                break

        if current_file:
            file_contents[current_file].append(line)

    # Write the contents to the corresponding files
    for filename, contents in file_contents.items():
        with open(filename, 'w') as f:
            f.writelines(contents)

if __name__ == '__main__':
    main()