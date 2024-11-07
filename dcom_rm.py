import sys

# Helper function to check if a string is in DD/MM/YYYY format.
def is_valid_date_format(part):
    if len(part) != 10:
        return False
    if not (part[0:2].isdigit() and part[3:5].isdigit() and part[6:].isdigit()):
        return False
    if not (part[2] == '/' and part[5] == '/'):
        return False
    return True

# Helper function to find a date pattern anywhere in a string
def contains_date(line):
    if len(line) < 10: return False
    for i in range(len(line) - 9):  # Check each substring of length 10
        potential_date = line[i:i+10]
        if is_valid_date_format(potential_date):
            return True
    return False

# Helper function to check if the first non-empty line of multiline comment contains a date
def first_line_contains_date(comment_lines):
    for line in comment_lines:
        stripped_line = line.strip()
        if stripped_line:  # Check the first non-empty line
            return contains_date(stripped_line)
    return False

# To determine if // is inside a string delimited by quotes " "
def check_slash_in_quotes(line):
    inside_quotes = False
    escaped = False
    
    for i in range(len(line) - 1):
        char = line[i]
        
        # Check if the current character is escaping the next character
        if char == '\\' and not escaped:  # The character is an escape only if it's not escaped itself
            escaped = True
            continue
        
        # Toggle the inside_quotes flag if encountering a quote that's not escaped
        if char == '"' and not escaped:
            inside_quotes = not inside_quotes
        
        # Check for "//" inside quotes
        if char == '/' and line[i + 1] == '/' and inside_quotes:
            return True
        
        if char == '/' and line[i + 1] == '*' and inside_quotes:
            return True
        
        # Reset escape flag
        escaped = False

    return False

# Function to handle single line comments start with "//"
def remove_dated_single_line_comments(line):
    if '//' in line:
        if check_slash_in_quotes(line):
            return line
        
        parts = line.split("//")
            # Check the entire line for a date
        if contains_date(parts[1]):
                # Skip this line if a date format is found
            return parts[0]
        else:
                # Add the line if no date is found
            return line
        # else:
        #     new_lines.append(line)
    return line

# Function to handle all comments
def remove_dated_comments(lines):
    new_lines = []
    in_multiline_comment = False
    multiline_comment_buffer = []
    for line in lines:
        # Handle single line comments start with "/*"
        if '/*' in line:  # Detect the start of a multiline comment
            if check_slash_in_quotes(line):
                new_lines.append(line)

            in_multiline_comment = True
            multiline_comment_buffer.append(line)
            if '*/' in line:  # If the comment starts and ends on the same line
                in_multiline_comment = False
                # Check if the first line of this single-line block contains a date
                if first_line_contains_date(multiline_comment_buffer):
                    # If the first line contains a date, don't add it to new_lines
                    multiline_comment_buffer = []
                else:
                    # If no date is found, add the whole block
                    new_lines.extend(multiline_comment_buffer)
                    multiline_comment_buffer = []
            continue
        
        # Handle multiline comments
        if in_multiline_comment:
            multiline_comment_buffer.append(line)
            if '*/' in line:  # End of the multiline comment
                in_multiline_comment = False
                # Now check if the first line of the multiline block contains a date
                if first_line_contains_date(multiline_comment_buffer):
                    # If the first line contains a date, don't add it to new_lines
                    multiline_comment_buffer = []
                    # if(connected_line):multiline_comment_buffer.append(after_comment)
                else:
                    # If no date is found, add the entire block to new_lines
                    new_lines.extend(multiline_comment_buffer)
                    multiline_comment_buffer = []
            continue
        
        # Handle single line comments start with "//"
        if not in_multiline_comment:
            new_lines.append(remove_dated_single_line_comments(line))
    return new_lines

def is_program_correct(file_path):
    try:
        with open(file_path, "r") as f:
            f.read()  # Just try reading the file, no compilation necessary
        return True
    except (FileNotFoundError, IOError):
        return False

# Main program
if len(sys.argv) == 3:
    input_file = sys.argv[1]
    output_file = sys.argv[2]

with open(input_file, "r") as f:
    lines = f.readlines()

if is_program_correct(input_file):
    without_dated_comments = remove_dated_comments(lines)

    # Write the final lines to the output file
    with open(output_file, "w") as f:
        f.writelines(without_dated_comments)
else:
    print("Program is incorrect")
