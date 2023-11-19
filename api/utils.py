import psutil
import subprocess


def find_process_id_by_path(script_name):
    """Find a process ID (PID) by the name of the Python script."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if any(script_name in cmd_part for cmd_part in proc.info['cmdline']):
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return None


def run_script(path):
    """Run a Python script from the given path."""
    try:
        subprocess.Popen(['python', path])
        print(f"Script {path} is now running.")
    except Exception as e:
        print(f"Failed to run script: {e}")


if __name__ == '__main__':
    # Example usage
    script_path = 'stream.py'
    pid = find_process_id_by_path(script_path)

    if pid:
        process = psutil.Process(pid)
        process.terminate()
        print(f"Process {pid} terminated.")
        run_script(script_path)
        print("Running again")
