# Python Interfaces for matRad
This repository contains python interfaces for running dose calculation and other functions
from the matRad codebase.

An updated/tested installation script is provided for linux systems that runs matrad on octave and installs all 
dependencies.
###  Heavily sourced from matRAD (https://github.com/e0404/matRad)


## Install Instructions
### matRad Installation

First fetch the submodule
```
git submodule update --init --recursive
```

For Linux systems,
```
cd matRad
bash before_install_linux.sh
```

The dependencies have been updated and are different from the ones on the matRad master. Warning: This has only been tested on linux operating systems


### Python wrapper dependencies
```
pip install -r requirements.txt
```

## Sample scripts

For sample scripts check the projects directory. This contains code used for different projects. 
Code can be found for gamma calculation, dose calculation etc. 

## Repo structure

```
- matrad # modified version of the matrad github repository at a specific commit 
- pyrad # interfaces, source code and utils for python interfaces for matrad
- projects # Example scripts for different purposes within a project
...

```


