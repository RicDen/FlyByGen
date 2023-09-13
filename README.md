<!--
 Copyright (c) 2023 Tartu University, Ric Dengel

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
 -->



# CometGen v1-0
This is a python blender tool creating various comet chapes in blender, render them and perform post processing to make
the images realistic. 

TODO: Major tasks are to be implemented. Such as:
1. Cleaning of not needed objects which just exist for the base template
2. Improvement of Dust jets


Before running script first time after boot log in to ssh and connect network drive
net use Z: \\to-nas.to.ee\OPIC 
Username: dengel_TO

TODO: Add scripts to run on laptop and desktop. Adapt git accordingly. git branch?
TODO: Add debug, error message features and log everything

out0002: Start 23-05-06_14:30
## Blender
Blender version used for development is 3.4. Please report if you managed to run other versions as well to state support here. 

## Documentation

### Where?
The documentation for this project is create with sphinx and can be found via
<!-- TODO: Add reference to extensive documentation -->

### How
adapt make.bat for windows systems or makefile for linux based systems to use the right sphinx build options when blender is part of the toolchain or not.
If blender is used in the toolchain, please adapt the path in line 8 of the makefile and make.bat to suit your blender path. 

### Requirements
To update the documentation of this project, there may be some additional software requirements:
#### For conda environment:
- sphinx: pip install sphinx
- sphinx_design: pip install sphinx_design
- furo for html: pip install furo
- numpy
- matplotlib


When blender is not being used:  -->

Start of architecture v0-2.


Requires sphinx installation

# Different configs
Laptop:
cache:
"cache_dir": ".\\cache",
"project_directory": "D:\\OneDrive - Tartu Ülikool\\Data Generation\\flyby_gen_v1-0",

Desktop:
cache:
"cache_dir": "Z:\\FLYBY_GEN\\cache\\",
"project_directory": "D:\\FlyByGen_Development\\flyby_gen",

<!-- FEATURE Create a way to write to the local drive the current project and then load to nas to make use of the faster local storage, but not overload it
-->


<!-- TODO: Analyse if all parameters are in the correct files. paths etc. -->

Json files cannot be updated during runtime before they have been loaded. They are loaded during the process and thus changing them during runtime (before the render starts) can lead to unwanted results

Modules:

      {
        "class_path": "src\\postProcessing\\Noise\\NoiseGen_basic.py",
        "module_name": "Noise",
        "class_name": "BasicNoiseGenerator"
      },