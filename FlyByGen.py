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

with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)

sys.path.append(paths['project_directory'])

# FEATURE: Enable multithreading and locking of json files while scene is generated
class FlyByGen:

    # BUG: Doesn't work yet, after entering the passwords, the program freezes and nothing happens
    # def connect_NAS():
    #     # Connecting for data dump
    #     # cmd_connect_NAS = f'net use Z: \\to-nas.to.ee\OPIC'
    #     # subprocess.run(cmd_connect_NAS, shell=True)
    #     # print("Connected NAS")

    # DOC: Add paths link to documentation
    def logging_setup(self):
        """
        Instantiates the logger and starts logging everything after the configuration is done

        :return: A Output Logger object used to run subprocesses with active logging.

        :rtype: obj[OutputLogger]

        """
        FlyGenLogger = OutputLogger(paths)
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
        blender_path = paths['blender_path']
        blend_file = paths['blend_file']
        bpy_controller = paths['bpy_controller']
        return f'"{blender_path}" -b "{blend_file}" -P "{bpy_controller}"'


    def set_post_processing_path(self):
        """
            Loads the commands from the json file and combines the blocks into a string which can be run by a subprocess

            :return: post processing subprocess execution command

            :rtype: [str]
        """
        post_controller_python = paths["post_controller_python"]
        post_processing_controller = paths['post_controller_path']
        return [post_controller_python, post_processing_controller]

    
    def __init__(self):

        FlyGenLogger = self.logging_setup()
        logging.info("Starting FlyByGen")
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
