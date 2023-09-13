import sys
import os
import subprocess
import logging
import json
import time
'''
Instructions:
To run the output logger 
    1. Initiate the Output Logger
    2. configure the logging
    3. Log / print where the file will be
    4. Run any subprocess etc which should be run with the logger
'''
# TODO: Add all comments


import os
import sys
import logging
import subprocess

class OutputLogger:
    def __init__(self, paths):
        self.project_directory = os.path.join(paths['cache_dir'], f"{paths['pipeline_version']}{paths['number_of_generation']}")
        self.log_directory = os.path.join(self.project_directory, paths['log_dir'])
        # 
        
    def create_log_file(self):
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
        logging.basicConfig(
            filename=self.log_file,
            filemode="w",
            level=logging.INFO,
            format="%(asctime)s - %(message)s"
        )

    def log_output_file(self):
        logging.info(f"Output is being logged to {self.log_file}")
        
    def run_subprocess(self, command):
        logging.info("Starting subprocess")

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            subprocess_logger = logging.getLogger("subprocess")
            subprocess_logger.setLevel(logging.INFO)
            subprocess_logger.addHandler(logging.StreamHandler())

            for line in process.stdout:
                line = line.strip()
                subprocess_logger.info(line)

            process.wait()

            if process.returncode != 0:
                logging.error(f"Subprocess failed with return code {process.returncode}")
        except Exception as e:
            logging.error(f"Error occurred during subprocess execution: {e}")





    
# with open('src/config/paths.json', 'r') as f:
#     paths = json.load(f)  
    
# log_dir = paths['log_dir'].format(
#     cache_dir=paths['cache_dir'],
#     pipeline_version=paths['pipeline_version'],
#     number_of_generation=paths['number_of_generation']
# )

# # Create an instance of the OutputLogger class
# logger = OutputLogger(log_dir)

# # Configure logging
# logger.configure_logging()

# # Run the subprocess and log its output
# logger.run_blender_subprocess()

# # Log to the file
# logger.log_output_file()
