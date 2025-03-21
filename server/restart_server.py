#!/usr/bin/env python3
import subprocess
import time
import os
import signal
import sys
import logging
import psutil

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('server-restart')


def kill_process_on_port(port):
    """Kill any process running on the given port."""
    try:
        # Find processes using the port
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        logger.info(
                            f"Killing process {proc.info['pid']} ({proc.info['name']}) on port {port}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        logger.error(f"Error killing process on port {port}: {e}")
    return False


def start_server_with_optimizations():
    """Start the server with optimizations applied."""
    # First run the optimization script
    try:
        logger.info("Running optimization script...")
        subprocess.run(["python", "optimize_server.py"], check=True)
    except Exception as e:
        logger.error(f"Failed to run optimizations: {e}")

    # Start the server with high priority
    # For Windows
    if os.name == 'nt':
        server_process = subprocess.Popen(["start", "/B", "/HIGH", "python", "app.py"],
                                          shell=True)
    # For Unix-like systems
    else:
        # Set environment variable for nice value
        env = os.environ.copy()
        env["PRIORITY"] = "-10"  # High priority
        server_process = subprocess.Popen(["nice", "-n", "-10", "python", "app.py"],
                                          env=env)

    logger.info(f"Server started with PID {server_process.pid}")
    return server_process


def main():
    # Kill any existing process on port 5050
    kill_process_on_port(5050)

    # Wait a moment to ensure port is released
    time.sleep(1)

    # Start the server with optimizations
    server_process = start_server_with_optimizations()

    try:
        # Keep the script running to maintain the server
        logger.info("Server restart script is now monitoring the server...")
        while True:
            time.sleep(5)

            # Check if server is still running
            if server_process.poll() is not None:
                logger.warning("Server has stopped. Restarting...")
                # Kill any remaining processes on the port
                kill_process_on_port(5050)
                time.sleep(1)
                # Restart
                server_process = start_server_with_optimizations()

    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        if os.name == 'nt':
            # Windows
            subprocess.run(["taskkill", "/F", "/PID", str(server_process.pid)])
        else:
            # Unix-like
            server_process.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
