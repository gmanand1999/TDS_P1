from flask import Flask, request, jsonify
import os
import subprocess
import json
import sqlite3
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# Define the base data directory
DATA_DIR = '/data'

@app.route('/run', methods=['POST'])
def run_task():
    task_description = request.args.get('task')
    
    try:
        # Parse the task description using an LLM (mocked here)
        if "install" in task_description and "datagen.py" in task_description:
            return install_and_run_datagen(task_description)
        elif "format" in task_description:
            return format_file(task_description)
        elif "count" in task_description:
            return count_wednesdays(task_description)
        elif "sort" in task_description:
            return sort_contacts(task_description)
        elif "recent" in task_description:
            return write_recent_logs(task_description)
        elif "index" in task_description:
            return create_index(task_description)
        elif "extract sender" in task_description:
            return extract_sender_email(task_description)
        elif "extract card number" in task_description:
            return extract_card_number(task_description)
        elif "similar comments" in task_description:
            return find_similar_comments(task_description)
        elif "total sales" in task_description:
            return calculate_total_sales(task_description)
        else:
            return jsonify({"error": "Task not recognized"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/read', methods=['GET'])
def read_file():
    file_path = request.args.get('path')
    full_path = os.path.join(DATA_DIR, file_path)

    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            content = f.read()
        return jsonify({"content": content}), 200
    else:
        return jsonify({}), 404

# Define the task functions
def install_and_run_datagen(task_description):
    # Install uv if not installed
    subprocess.run(['pip', 'install', 'uv'], check=True)
    user_email = extract_email_from_task(task_description)  # Mocked function
    subprocess.run(['python', 'datagen.py', user_email], check=True)
    return jsonify({"message": "Data generation completed."}), 200

def format_file(task_description):
    # Format the file using prettier
    file_path = extract_file_path(task_description)  # Mocked function
    subprocess.run(['prettier', '--write', os.path.join(DATA_DIR, file_path)], check=True)
    return jsonify({"message": "File formatted."}), 200

def count_wednesdays(task_description):
    file_path = extract_file_path(task_description)  # Mocked function
    with open(os.path.join(DATA_DIR, file_path), 'r') as f:
        dates = f.readlines()
    wednesdays_count = sum(1 for date in dates if datetime.strptime(date.strip(), '%Y-%m-%d').weekday() == 2)
    with open(os.path.join(DATA_DIR, 'dates-wednesdays.txt'), 'w') as f:
        f.write(str(wednesdays_count))
    return jsonify({"message": "Count of Wednesdays written."}), 200

def sort_contacts(task_description):
    file_path = extract_file_path(task_description)  # Mocked function
    with open(os.path.join(DATA_DIR, file_path), 'r') as f:
        contacts = json.load(f)
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))
    with open(os.path.join(DATA_DIR, 'contacts-sorted.json'), 'w') as f:
        json.dump(sorted_contacts, f)
    return jsonify({"message": "Contacts sorted."}), 200

def write_recent_logs(task_description):
    log_files = sorted([f for f in os.listdir(os.path.join(DATA_DIR, 'logs')) if f.endswith('.log')], key=lambda x: os.path.getmtime(os.path.join(DATA_DIR, 'logs', x)), reverse=True)
    recent_lines = []
    for log_file in log_files[:10]:
        with open(os.path.join(DATA_DIR, 'logs', log_file), 'r') as f:
            recent_lines.append(f.readline().strip())
    with open(os.path.join(DATA_DIR, 'logs-recent.txt'), 'w') as f:
        f.write('\n'.join(recent_lines))
    return jsonify({"message": "Recent log lines written."}), 200

def create_index(task_description):
    md_files = [f for f in os.listdir(os.path.join(DATA_DIR, 'docs')) if f.endswith('.md')]
    index = {}
    for md_file in md_files:
        with open(os.path.join(DATA_DIR, 'docs', md_file), 'r') as f:
            for line in f:
                if line.startswith('#'):
                    index[md_file] = line[1:].strip()  # Extract title
                    break
    with open(os.path.join(DATA_DIR, 'index.json'), 'w') as f:
        json.dump(index, f)
    return jsonify({"message": "Index created."}), 200

def extract_sender_email(task_description):
    with open(os.path.join(DATA_DIR, 'email.txt'), 'r') as f:
        email_content = f.read()
    # Mock LLM extraction
    sender_email = "extracted@example.com"  # Replace with actual extraction logic
    with open(os.path.join(DATA_DIR, 'email-sender.txt'), 'w') as f:
        f.write(sender_email)
    return jsonify({"message": "Sender email extracted."}), 200

def extract_card_number(task_description):
    # Mock LLM extraction
    card_number = "1234567890123456"  # Replace with actual extraction logic
    with open(os.path.join(DATA_DIR, 'credit-card.txt'), 'w') as f:
        f.write(card_number.replace(" ", ""))
    return jsonify({"message": "Card number extracted."}), 200

def find_similar_comments(task_description):
    with open(os.path.join(DATA_DIR, 'comments.txt'), 'r') as f:
        comments = f.readlines()
    # Mock similarity check
    most_common_pair = Counter(comments).most_common(1)[0]  # Replace with actual similarity logic
    with open(os.path.join(DATA_DIR, 'comments-similar.txt'), 'w') as f:
        f.write('\n'.join(most_common_pair))
    return jsonify({"message": "Similar comments found."}), 200

def calculate_total_sales(task_description):
    conn = sqlite3.connect(os.path.join(DATA_DIR, 'ticket-sales.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(price * units) FROM tickets WHERE type = 'Gold'")
    total_sales = cursor.fetchone()[0]
    with open(os.path.join(DATA_DIR, 'ticket-sales-gold.txt'), 'w') as f:
        f.write(str(total_sales))
    conn.close()
    return jsonify({"message": "Total sales calculated."}), 200

if __name__ == '__main__':
    app.run(debug=True)