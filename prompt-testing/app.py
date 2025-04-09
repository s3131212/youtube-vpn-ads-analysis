from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from task_manager import TaskManager  # Import task manager
from werkzeug import serving
import re
from flask import abort
from hashlib import sha256

app = Flask(__name__)
app.secret_key = 'To be or youtube'  # Required to use Flask sessions
# Simple login required decorator
def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['logged_in']:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.', 'error')
            return redirect(url_for('login'))
    wrap.__name__ = f.__name__  # Required for Flask to properly handle routes with decorators
    return wrap

# Initialize task manager and start the background worker
task_manager = TaskManager()
task_manager.start_worker()


# 允許的 IP 範圍
ALLOWED_IP_PREFIX = "140.112."

# 自定義的 IP 檢查函數
def is_allowed_ip(ip_address):
    # return True
    return ip_address.startswith(ALLOWED_IP_PREFIX)

# 限制訪問的路由
@app.before_request
def limit_remote_addr():
    client_ip = request.remote_addr  # 取得訪客的 IP 位址
    if not is_allowed_ip(client_ip):
        abort(403)  # 如果不是允許的 IP，返回 403 Forbidden

@app.route('/')
@login_required
def index():
    # Homepage to upload a prompt
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_prompt():
    # print(request.form)
    author = request.form['author']
    if 'single_prompt' in request.form:
        single = True
        prompt = ['This prompt will not be used.', request.form['prompt_vpn']]
    else :
        single = False
        prompt = [request.form['prompt_ad'], request.form['prompt_vpn']]
    task_manager.add_prompt(author, single, prompt)  # Add the prompt to the task manager queue
    return redirect(url_for('history'))

@app.route('/history')
@login_required
def history():
    # Get all prompts and their results
    tasks = task_manager.get_all_tasks()
    return render_template('history.html', tasks=tasks)


@app.route('/get_results', methods=['GET'])
def get_results():
    # Return results in JSON format
    tasks = task_manager.get_all_tasks()
    return jsonify(tasks)

@app.route('/task/<task_id>', methods=['GET'])
@login_required
def get_task_by_id(task_id):
    # Fetch the task by its ID
    task = task_manager.get_task_by_id(task_id)
    if task:
        # Render the score page using the fetched task data
        return render_template('score_page.html', task=task)
    else:
        return render_template('error.html', message="Task not found"), 404


@app.route('/task_status')
@login_required
def task_status():
    # Return the current status of tasks
    tasks = task_manager.get_all_tasks()
    return jsonify(tasks)

#### Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if the pass key is correct
        entered_pass_key = request.form['pass_key']
        if sha256(entered_pass_key.encode()).digest() == b'\x9f\x86\xd0\x81\x88L}e\x9a/\xea\xa0\xc5Z\xd0\x15\xa3\xbfO\x1b+\x0b\x82,\xd1]l\x15\xb0\xf0\n\x08':
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to the homepage after login
        else:
            flash('Incorrect pass key, try again.', 'error')
            return render_template('login.html', title="Login")

    return render_template('login.html', title="Login")

### Filter task_status
parent_log_request = serving.WSGIRequestHandler.log_request
def log_request(self, *args, **kwargs):
    if self.path == '/task_status':
        return

    parent_log_request(self, *args, **kwargs)

def filter_task_status_logs():
    serving.WSGIRequestHandler.log_request = log_request

if __name__ == '__main__':
    filter_task_status_logs()
    app.run(debug=False, host='0.0.0.0', threaded=True)
