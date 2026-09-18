### Export virtual environment

! Before exporting a virtual environment, always make sure, your changes/new dependencies build from the most recent version on git, to prevent conflicts of multiple parrallel venv configs.

Preferred method with conda:
1. `conda env export > environment.yml`
2. remove the `prefix` field from the file
3. remove the dependencie to local packages
   1. the line `enparto==0.1.0` under `dependecies/pip` 

alternativly for just exporting pip dependencies:
1. `pip list --format=freeze > requirements.txt`
2. remove the dependencie to local packages
   1. the line `enparto==0.1.0`