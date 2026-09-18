import os
from datetime import datetime

import yaml


def load_params_from_yaml(yaml_file_paths):
    """
    Loads parameters from multiple YAML files and returns them as a single dictionary.

    Args:
        yaml_file_paths (list of str): List of paths to YAML files.

    Returns:
        dict: Loaded parameters from all YAML files combined into one dictionary.
    """
    params = {}

    for file_path in yaml_file_paths:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                file_params = yaml.safe_load(f)

                params = deep_merge(params, file_params)
        else:
            print(f"Warning: File {file_path} does not exist!")

    return convert_values(params)


def deep_merge(dict1, dict2):
    """
    Recursively merges two dictionaries. The second dictionary's values overwrite the first one
    in case of conflicts.

    Args:
        dict1 (dict): The first dictionary.
        dict2 (dict): The second dictionary to merge.

    Returns:
        dict: The merged dictionary.
    """
    for key, value in dict2.items():
        if isinstance(value, dict) and key in dict1:
            dict1[key] = deep_merge(dict1[key], value)
        else:
            dict1[key] = value
    return dict1


def convert_values(data):
    """
    Recursive function that walks through the JSON structure and, if necessary,
    converts datetime strings into datetime objects.

    Args:
        data (dict or list): The data object to convert.

    Returns:
        dict/list: The converted data object where datetime strings
                   are converted into datetime objects.
    """
    if isinstance(data, dict):
        return {key: convert_values(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_values(item) for item in data]
    elif isinstance(data, str):
        try:
            return datetime.fromisoformat(data)
        except ValueError:
            return data
    else:
        return data
