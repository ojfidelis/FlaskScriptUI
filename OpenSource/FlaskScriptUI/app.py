from flask import Flask, render_template, redirect, url_for, Response
import subprocess
import os

app = Flask(__name__)

# Path to the Python script you want to run
SCRIPT_PATH = "/FlaskScriptUI/script.py"

# Global process handle
process = None


@app.route('/')
def index():
    """Main page to show the button and the state of the script."""
    return render_template('index.html')


@app.route('/toggle')
def toggle():
    """Start or stop the Python script based on current state."""
    global process
    if process is None:
        # Start the Python script with unbuffered output
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"  # Force unbuffered output
        process = subprocess.Popen(["python", SCRIPT_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   bufsize=1)
        print(f"Started script with PID: {process.pid}")
    else:
        # Stop the Python script safely on Windows
        process.terminate()  # Terminate the process on Windows
        process = None
        print("Script stopped.")

    return redirect(url_for('index'))


@app.route('/stream')
def stream():
    """Stream the output of the script."""

    def generate():
        global process
        if process is not None and process.poll() is None:  # Only stream if process is running
            while process.poll() is None:  # While the process is still running
                output = process.stdout.readline()
                error = process.stderr.readline()

                if output:
                    yield f"data: {output}\n\n"
                if error:
                    yield f"data: ERROR: {error}\n\n"
        else:
            yield f"data: Script stopped.\n\n"  # Send "Script stopped" once when the process is stopped

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)
