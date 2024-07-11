# Folder Synch Script:

This Python script synchronizes two directories (source and replica), ensuring that the replica directory is an exact copy of the source directory. It uses MD5 hashes to compare files and logs all operations to a specified log file. 

## Features

- Calculate MD5 hashes for files to determine differences.
- Synchronize files and directories from source to replica.
- Create missing directories in the replica.
- Remove directories and files in the replica that are not in the source.
- Copy new or updated files from source to replica.
- Supports nested subdirectories.
- Log all operations for easy tracking.
- Set synchronization interval for periodic updates.
- If the source dir does not exist, it raises an error.
- If the replica dir does not exist, it creates it.
- To stop the script use keyboard interrupt "CTRL+C"

## Prerequisites

- Python 3.6 or higher

## Libraries (All built in python)
- os
- hashlib
- shutil
- logging
- argparse
- time

### Command-Line Arguments
- `--source`(required): Path to the source directory.
- `--replica`(required): Path to the replica directory.
- `--log_file`(required): Path to the log file.
- `--synch_interval`(required): Time interval for synchronization in seconds.

## Usage
python main.py [--source SOURCE] [--replica REPLICA] [--log_file LOG_FILE] [--synch_interval SYNCH_INTERVAL]

## Example
python folder_synch.py --source "path/to/source" --replica "path/to/replica" --log_file "path/to/log_file.txt" --synch_interval "60" 
