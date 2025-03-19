import os
import subprocess
import platform
import time

def kill_python_processes():
    """Kill any running Python processes"""
    system = platform.system()
    
    if system == 'Windows':
        # Windows command to list and kill Python processes
        os.system('taskkill /f /im python.exe')
    else:
        # Linux/Mac command
        os.system("pkill -f python")
    
    # Wait a moment for processes to terminate
    time.sleep(1)

def main():
    print("Killing any existing Python processes...")
    kill_python_processes()
    
    print("Starting Flask server on port 5050...")
    # Start the Flask server in a new process
    subprocess.Popen(["python", "app.py"])
    
    print("Server should now be running. Check for any errors in the console.")

if __name__ == "__main__":
    main() 