import psutil
import subprocess
import time
import insightface


def get_face_encoding(img_np):
    # Initialize the InsightFace model for CPU usage
    model = insightface.app.FaceAnalysis()
    model.prepare(ctx_id=-1)  # ctx_id=-1 indicates CPU mode

    # Perform face analysis (detection, alignment, recognition)
    faces = model.get(img_np)

    if len(faces) == 0:
        print("No face found")
        return None

    # Extracting face encodings
    face_encodings = [face.normed_embedding for face in faces]
    return face_encodings


def find_process_id_by_path(script_name):
    """Find a process ID (PID) by the name of the Python script."""
    print("Searching for script:", script_name)
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                # Print details of Python processes
                print("Python process:", proc.info['pid'], proc.info['cmdline'])
                if script_name in proc.info['cmdline']:
                    print("Found PID: ", proc.info['pid'])
                    return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None


def run_script(path):
    """Run a Python script from the given path."""
    try:
        # If using a specific version of Python or a virtual environment, specify the path here
        subprocess.Popen(['python', path])
        print(f"Script {path} is now running.")
    except Exception as e:
        print(f"Failed to run script: {e}")


if __name__ == '__main__':
    script_path = 'stream.py'

    # Optionally introduce a delay to ensure process starts
    time.sleep(2)

    pid = find_process_id_by_path(script_path)

    if pid:
        process = psutil.Process(pid)
        process.terminate()
        print(f"Process {pid} terminated.")
        run_script(script_path)
        print("Running again")
    else:
        print("No matching PID found.")
