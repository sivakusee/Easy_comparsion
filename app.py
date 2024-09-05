from flask import Flask, render_template, request
import difflib
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def highlight_differences(line1, line2):
    matcher = difflib.SequenceMatcher(None, line1, line2)
    result1 = []
    result2 = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result1.append(line1[i1:i2])
            result2.append(line2[j1:j2])
        elif tag == 'replace':
            result1.append(f'<span class="changed-word">{line1[i1:i2]}</span>')
            result2.append(f'<span class="changed-word">{line2[j1:j2]}</span>')
        elif tag == 'delete':
            result1.append(f'<span class="changed-word">{line1[i1:i2]}</span>')
        elif tag == 'insert':
            result2.append(f'<span class="changed-word">{line2[j1:j2]}</span>')

    return ''.join(result1), ''.join(result2)

def compare_texts(text1, text2):
    text1_lines = text1.splitlines()
    text2_lines = text2.splitlines()
    matcher = difflib.SequenceMatcher(None, text1_lines, text2_lines)
    formatted_diff1 = []
    formatted_diff2 = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for line1, line2 in zip(text1_lines[i1:i2], text2_lines[j1:j2]):
                formatted_diff1.append(line1)
                formatted_diff2.append(line2)
        elif tag == 'replace':
            for line1, line2 in zip(text1_lines[i1:i2], text2_lines[j1:j2]):
                hl1, hl2 = highlight_differences(line1, line2)
                formatted_diff1.append(f'<span class="changed-line">{hl1}</span>')
                formatted_diff2.append(f'<span class="changed-line">{hl2}</span>')
        elif tag == 'delete':
            for line in text1_lines[i1:i2]:
                formatted_diff1.append(f'<span class="deleted-line">{line}</span>')
                formatted_diff2.append('')
        elif tag == 'insert':
            for line in text2_lines[j1:j2]:
                formatted_diff1.append('')
                formatted_diff2.append(f'<span class="added-line">{line}</span>')

    # # Handle remaining lines if files are of different lengths
    # remaining_lines1 = text1_lines[len(formatted_diff1):]
    # remaining_lines2 = text2_lines[len(formatted_diff2):]
    #
    # if remaining_lines1:
    #     for line in remaining_lines1:
    #         formatted_diff1.append(f'<span class="deleted-line">{line}</span>')
    #         formatted_diff2.append('')
    # elif remaining_lines2:
    #     for line in remaining_lines2:
    #         formatted_diff1.append('')
    #         formatted_diff2.append(f'<span class="added-line">{line}</span>')

    return '\n'.join(formatted_diff1), '\n'.join(formatted_diff2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    file1 = request.files['file1']
    file2 = request.files['file2']

    text1 = file1.read().decode('utf-8')
    text2 = file2.read().decode('utf-8')
    diff1, diff2 = compare_texts(text1, text2)
    return render_template('index.html', diff1=diff1, diff2=diff2)

if __name__ == '__main__':
    app.run(debug=True)
