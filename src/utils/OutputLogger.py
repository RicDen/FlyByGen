import sys
import os
import subprocess
import logging
import json
import time

class OutputLogger:
    """
    Instructions:
    To run the output logger 
        1. Initiate the Output Logger
        2. configure the logging
        3. Log / print where the file will be
        4. Run any subprocess etc which should be run with the logger
    """
    def __init__(self, paths):
        if not os.path.exists(paths['cache_dir']):
            os.mkdir(paths['cache_dir'])
            print(f"Created cache dir")
        self.project_directory = os.path.join(paths['cache_dir'], f"{paths['pipeline_version']}{paths['number_of_generation']}")
        self.log_directory = os.path.join(self.project_directory, paths['log_dir'])
        
    def create_log_file(self):
        """
        Creates a new log file for each pipeline run 
        and the according file structure        
        """

        # Check if the directory already exists
        if not os.path.exists(self.project_directory):
            os.mkdir(self.project_directory)
            
        if not os.path.exists(self.log_directory):
            os.mkdir(self.log_directory)
        
        existing_logs = [filename for filename in os.listdir(self.log_directory) if filename.endswith('.log')]

        # Define a new number for the log file
        new_number = 1

        # Find the next available number for the log file
        while f"log_{new_number}.log" in existing_logs:
            new_number += 1

        # Create new log file
        log_filename = f"log_{new_number}.log"
        self.log_file = os.path.join(self.log_directory, log_filename)
         
        # return log_path

    def configure_logging(self):
        """
            Configures the logging functionalities
            Each logging message is stored with a timestamp
        """
        logging.basicConfig(
        filename=self.log_file,
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s - %(message)s"
        )

    def log_output_file(self):
        """
            Adds logging message about log file path
        """
        logging.info(f"Output is being logged to {self.log_file}")
        
    def run_subprocess(self, command):
        """
            Running a subprocess with the correct logging setup

            :param command: Defines the command to be executed by the subprocess
            :type: str
        """
        logging.info("Starting subprocess")
        print(f"Sub process: {command}")
        # BUG: Subprocesses don't terminate in Linux use subprocess.Popen on windows and subprocess.

        try:
            # BUG: Subprocesses don't terminate in Linux use:
            # process = subprocess.run(
            # Windows:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,  # This replaces universal_newlines=True in Python 3.7 and later
                # check=False,  # Allow the process to complete even if the return code is non-zero
            )

            subprocess_logger = logging.getLogger("subprocess")
            subprocess_logger.setLevel(logging.INFO)
            subprocess_logger.addHandler(logging.StreamHandler())

            # for line in process.stdout.splitlines():
            # Windows:
            for line in process.stdout: # 
                line = line.strip()
                subprocess_logger.info(line)

            # BUG: Subprocesses don't terminate in Linux use:
            # return_code = process.returncode
            # Windows:
            process.wait()

            if return_code == 0:
                logging.info("Subprocess finished successfully.")
            else:
                logging.error(f"Subprocess failed with return code {return_code}")

            if process.returncode != 0:
                logging.error(f"Subprocess failed with return code {process.returncode}")
        except Exception as e:
            logging.error(f"Error occurred during subprocess execution: {e}")
