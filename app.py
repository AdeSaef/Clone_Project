from flask import Flask, render_template, request
import re

app = Flask(__name__)

# Function to process the input and split it into groups of questions, points, and answers
def process_input(input_text):
    lines = input_text.strip().split("\n")
    output_html = ""
    current_group = {}
    
    for idx, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Detect questions (lines with ')' or lines longer than 4 characters)
        if re.search(r'\d+\)', line) or len(line) > 4:
            # Merge lines if another question follows
            if "question" in current_group:
                current_group["question"] += "<br>" + line
            else:
                current_group["question"] = line
        
        # Detect the key (with "*") and points
        elif "*" in line:
            current_group["key"] = line  # key detection
            if idx + 1 < len(lines):
                current_group["points"] = lines[idx + 1].strip()  # points are on the next line
            continue  # skip the next line since it's part of points
        
        # Detect the image line
        elif "Gambar Tanpa Teks" in line:
            current_group["image"] = '<img src="untitled" alt="image"/>' 
            
        # Detect answers
        elif line == "a":
            current_group["answer_type"] = "essay"
        elif len(line) <= 5 and ")" not in line:
            # Collect answers but only process if we have at least 4 options
            if "answers" not in current_group:
                current_group["answers"] = []
            current_group["answers"].append(line)

        # When group is complete (end of question block)
        if "points" in current_group and ("answers" in current_group or current_group.get("answer_type") == "essay"):
            # Only process answers if we have at least 4 options
            if len(current_group.get("answers", [])) >= 4:
                output_html += format_group(current_group)
                current_group = {}  # reset for the next group

    # In case the last group does not get added due to missing points
    if current_group:
        if len(current_group.get("answers", [])) >= 4 or current_group.get("answer_type") == "essay":
            output_html += format_group(current_group)

    return output_html

# Function to format the group into HTML
def format_group(group):
    html = '<div class="mb-6 p-4 bg-white rounded-md shadow-md border border-gray-300">\n'
    
    # Add question
    if "question" in group:
        html += f'<p class="text-lg font-semibold">{group["question"]}</p>\n'
    
    # Add key and points in red
    if "key" in group and "points" in group:
        html += f'<p class="text-sm text-red-500">{group["key"]} {group["points"]}</p>\n'

    # Add image if present
    if "image" in group:
        html += f'{group["image"]}\n'

    # Add answers (radio buttons or text input for essay)
    if group.get("answer_type") == "essay":
        html += '<input type="text" class="w-full border rounded-lg p-2 mt-4" placeholder="Enter your answer"/>\n'
    elif "answers" in group:
        for i, answer in enumerate(group["answers"], start=1):
            html += f'<div><input type="radio" name="q{len(group["answers"])}" value="{answer}"> {answer}</div>\n'

    html += '</div>\n'
    return html

# Route for the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form['input_text']
        # Process the input and convert it to HTML
        output_html = process_input(input_text)
        return render_template('template.html', output_html=output_html)
    return render_template('index.html')

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
