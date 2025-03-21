#!/usr/bin/env python3
"""
Utility script to optimize server performance during video processing.
Run this before starting the server to apply optimizations.
"""

import os
import sys
import platform
import psutil
import subprocess
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('server-optimizer')


def set_process_priority():
    """Set the process priority to high for better performance."""
    try:
        # Get the current process
        process = psutil.Process(os.getpid())

        # Set high priority - platform dependent
        if platform.system() == "Windows":
            process.nice(psutil.HIGH_PRIORITY_CLASS)
            logger.info("Set process priority to HIGH_PRIORITY_CLASS")
        else:
            # For Unix-like systems (Linux, macOS)
            process.nice(-10)  # Lower values = higher priority
            logger.info("Set process nice value to -10 (higher priority)")
    except Exception as e:
        logger.error(f"Failed to set process priority: {e}")


def clear_temp_files():
    """Clear temporary files from previous runs."""
    try:
        # Clear temporary download directories
        patterns = ["temp_download_*",
                    "temp_tracked_video_*", "temp_*_short_*"]
        deleted_count = 0

        for pattern in patterns:
            temp_dirs = [d for d in os.listdir('.') if os.path.isdir(
                d) and d.startswith(pattern.replace('*', ''))]
            for temp_dir in temp_dirs:
                try:
                    logger.info(f"Removing temporary directory: {temp_dir}")
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to remove {temp_dir}: {e}")

        logger.info(f"Cleared {deleted_count} temporary directories")
    except Exception as e:
        logger.error(f"Error clearing temporary files: {e}")


def optimize_ffmpeg():
    """Configure ffmpeg for optimal performance."""
    try:
        # Create or modify ffmpeg configuration for better thread usage
        ffmpeg_config = os.path.expanduser("~/.ffmpeg-config")
        with open(ffmpeg_config, 'w') as f:
            f.write("# FFmpeg optimization settings\n")
            f.write(f"FFREPORT=file=ffreport.log:level=32\n")
            f.write(f"FFMPEG_THREADS={psutil.cpu_count()}\n")

        logger.info(f"Created ffmpeg optimization config: {ffmpeg_config}")

        # Set environment variables for the current process
        os.environ["FFREPORT"] = "file=ffreport.log:level=32"
        os.environ["FFMPEG_THREADS"] = str(psutil.cpu_count())

        logger.info(f"Set FFMPEG_THREADS to {psutil.cpu_count()}")
    except Exception as e:
        logger.error(f"Failed to optimize ffmpeg: {e}")


def check_disk_space():
    """Check and report available disk space."""
    try:
        # Get disk usage of current directory
        disk_usage = shutil.disk_usage('.')
        free_space_gb = disk_usage.free / (1024 * 1024 * 1024)

        logger.info(f"Available disk space: {free_space_gb:.2f} GB")

        if free_space_gb < 10:
            logger.warning(
                f"Low disk space! Only {free_space_gb:.2f} GB available. Processing may fail.")
    except Exception as e:
        logger.error(f"Failed to check disk space: {e}")


def main():
    """Run all optimizations."""
    logger.info("Starting server optimization...")

    # Clear temp files
    clear_temp_files()

    # Set process priority
    set_process_priority()

    # Optimize ffmpeg
    optimize_ffmpeg()

    # Check disk space
    check_disk_space()

    logger.info(
        "Server optimization completed. Start your server now for better performance.")


if __name__ == "__main__":
    main()
