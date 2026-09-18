# Setup
## Installing all requirements
### Python

This project uses Python 3.12.2.
Link: [https://www.python.org/downloads/release/python-3122/](https://www.python.org/downloads/release/python-3122/)

Create new virtual environment:
(execute following command in project root)
1. Create conda virtual environment: `conda env create -f environment.yml`
2. Build local package: `pip install -e .`
   
Update virtual environment: 
1. pull the latest version of `environment.yml` from the git repo
2. Update conda venv once already installed: `conda env update -f environment.yml --prune`

### Coding standards

Please use Black (code formatting) and Flake8 (linter).