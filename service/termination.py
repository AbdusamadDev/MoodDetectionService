import psutil


def find_process_id_by_path(script_name):
    """Find a process ID (PID) by the name of the Python script."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if any(script_name in cmd_part for cmd_part in proc.info['cmdline']):
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None


script_name = 'loop.py'
pid = find_process_id_by_path(script_name)
print(f"PID Found: {pid}")

if pid:
    process = psutil.Process(pid)
    process.terminate()
    print(f"Process {pid} terminated.")
else:
    print("Process not found.")
