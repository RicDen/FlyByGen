#  Copyright (c) 2023 Tartu University, Ric Dengel

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
The starting file is the FlyByGen.py. 
It is responsible for configuration of the project.

This includes:

- Logging tools to enable log files of the process

- Starting of all subprocess which are the building blocks of the project.

:param paths: The Path paramter is a globally defined parameter defined in src/config/paths.json file.
    The parameter is imported to each file through the json file and thus does not require to be used as function paramter.

"""

from src.utils.OutputLogger import OutputLogger
import json
import sys
import os
import logging
import shutil
import subprocess
import time

# BUG: Subprocesses don't terminate in Linux
# from src.utils.setup import SetUp
# import signal
# import psutil

# FEATURE: Enable multithreading and locking of json files while scene is generated
class FlyByGen:


    def init_for_os(self):
        
        # Determine the operating system
        current_os = os.name  # 'nt' for Windows, 'posix' for Linux

        # Load the appropriate path file based on the operating system
        if current_os == 'nt':  # Windows
            path_file = 'src/config/windows/paths.json'
            modules_blender_file = 'src/config/windows/modules_blender.json'
            modules_post_file = 'src/config/windows/modules_post.json'
        elif current_os == 'posix':  # Linux
            path_file = 'src/config/linux/paths.json'
            modules_blender_file = 'src/config/linux/modules_blender.json'
            modules_post_file = 'src/config/linux/modules_post.json'
        else:
            raise Exception(f"Unsupported operating system: {current_os}")

        # Destination path file (common for both OS)
        active_path_file = 'src/config/paths.json'
        active_modules_blender_file = 'src/config/modules_blender.json'
        active_modules_post_file = 'src/config/modules_post.json'

        # Copy the content of the source path file to the destination path file
        shutil.copyfile(path_file, active_path_file)
        shutil.copyfile(modules_blender_file, active_modules_blender_file)
        shutil.copyfile(modules_post_file, active_modules_post_file)

        with open('src/config/paths.json', 'r') as f:
            self.paths = json.load(f)

        sys.path.append(self.paths['project_directory'])


    # DOC: Add paths link to documentation
    def logging_setup(self):
        """
        Instantiates the logger and starts logging everything after the configuration is done

        :return: A Output Logger object used to run subprocesses with active logging.

        :rtype: obj[OutputLogger]

        """
        FlyGenLogger = OutputLogger(self.paths)
        FlyGenLogger.create_log_file()
        FlyGenLogger.configure_logging()
        FlyGenLogger.log_output_file()
        return FlyGenLogger

    # DOC: Add paths link to documentation
    # FEATURE: Allow for more modular backend. Command should not be defined here. Define fully in json?
    # FEATURE: Enable different logging levels and implement according messages

    def set_blender_paths(self):
        """
        Loads the commands from the json file and combines the blocks into a string which can be run by a subprocess

        :return: Blender subprocess execution command

        :rtype: [str]

        """
        blender_path = self.paths['blender_path']
        blend_file = self.paths['blend_file']
        bpy_controller = self.paths['bpy_controller']
        
        # return [blender_path, "-b", blend_file, "-P", bpy_controller]
        return [blender_path, "-b", blend_file, "-P", bpy_controller]


    def set_post_processing_path(self):
        """
            Loads the commands from the json file and combines the blocks into a string which can be run by a subprocess

            :return: post processing subprocess execution command

            :rtype: [str]
        """
        post_controller_python = self.paths["post_controller_python"]
        post_processing_controller = self.paths['post_controller_path']
        return [post_controller_python, post_processing_controller]

    # BUG: Subprocesses don't terminate in Linux
    # def cleanup_processes(self):
    #     # Check for and terminate any remaining subprocesses
    #     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    #         if 'blender' in proc.info['cmdline']:
    #             logging.warning(f"Terminating detached Blender process: {proc.info['pid']}")
    #             try:
    #                 proc.terminate()
    #             except psutil.NoSuchProcess:
    #                 pass

    def __init__(self):
        self.init_for_os()
        FlyGenLogger = self.logging_setup()
        # BUG: Subprocesses don't terminate in Linux
        # main_setup = SetUp()
        # main_setup.check_libraries()
        # signal.signal(signal.SIGTERM, self.cleanup_processes)
        logging.info("Starting FlyByGen")
        start_time = time.time()
        # Running blender graphics generator
        blender_command = self.set_blender_paths()
        FlyGenLogger.run_subprocess(blender_command)

# Need funtion which exectues the subprocess after the parameter range and increments files as defined in function parameter
# The cache and output paths need to be automatically update accordingly (maybe add date)

        


        blender_time = time.time()
        # # Running python post processing
        # post_process_command = self.set_post_processing_path()
        # FlyGenLogger.run_subprocess(post_process_command)
        post_time = time.time()
        render = blender_time-start_time
        post_processing_time = post_time-blender_time
        total_time = post_time-start_time
        logging.info(f"Render took: {int(render/60)}min {render%60}s")
        logging.info(f"Post processing took: {int(post_processing_time/60)}min {(post_processing_time%60)}s")
        logging.info(f"Pipeline ran for: {int(total_time/60)}min {total_time%60}s")
        logging.info("Finished everything")


print("Starting FlyByGen!")
FlyByGen()
