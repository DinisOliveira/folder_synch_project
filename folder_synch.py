import os
import hashlib
import shutil
import logging
import argparse
import time


def calculate_hash(file_path):
    '''Calculate MD5 hash of the file'''
    md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        #Reading the file in chunks to not overload memory in case there are big files
        while chunk := file.read(8192):
            md5.update(chunk)
    return md5.hexdigest()


def update_hash_dict(file_path, rel_path, hash_dict):
    '''Updates hashes dictionary with the file hash:'''
    hash = calculate_hash(file_path)
    if hash in hash_dict:
        hash_dict[hash].append(rel_path)
    else:
        hash_dict[hash] = [rel_path]


def dict_hashes(path, hash_dict_main, hash_dict_sub):
    '''Generates hashes for the files in a directory and its subdirectories and updates the hash dictionaries'''
    for filename in os.listdir(path):
        #Using os.listdir() in case there are no subdirectories since it's less process intensive because it only lists through the current directory
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            update_hash_dict(file_path, filename, hash_dict_main)
        elif os.path.isdir(file_path):
            #Using os.walk() in case there are subdirectories to be able to transverse the the directory and it's subdirectories
            for dir, _, files in os.walk(file_path):
                for sub_file in files:
                    sub_file_path = os.path.join(dir, sub_file)
                    rel_sub_path_file = os.path.relpath(sub_file_path, path)
                    update_hash_dict(sub_file_path, rel_sub_path_file, hash_dict_sub)

def ls_dir(path, sub_dir_files):
    '''Lists directories and files, associating each directory name with their relative file paths in a dictionary'''
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isdir(file_path):
            for dir, _, files in os.walk(path):
                relative_dir = os.path.relpath(dir, path)
                if relative_dir == ".":
                    relative_dir = "source"
                sub_dir_files[relative_dir] = []
                for file in files:
                        relative_path = os.path.relpath(os.path.join(dir, file), path)                      
                        sub_dir_files[relative_dir].append(relative_path)


def create_remove_sub_folders(source_dirs, replica_dirs, s_path, d_path):
    '''Create and remove subdirectories in replica to match source's structure'''
    source_dirs.pop('source', None)
    replica_dirs.pop('source', None)
    #Create missing directories in replica
    for sub_dir in source_dirs.keys():  
        destination_dir_path = os.path.join(d_path, sub_dir)
                
        if not os.path.exists(destination_dir_path):
            os.makedirs(destination_dir_path)
            log_message = (f"created {destination_dir_path}")
            logging.info(log_message)
            print(log_message)

    #Remove directories in replica that are not in source
    for sub_dir in replica_dirs.keys():
            source_dir_path = os.path.join(s_path, sub_dir)
            remove_path = os.path.join(d_path, sub_dir)
            
            if not os.path.exists(source_dir_path):
                shutil.rmtree(remove_path)
                log_message = f"Removed {remove_path}"
                logging.info(log_message)
                print(log_message)



def copy_files(source_hashes, dest_hashes, s_path, d_path):
    '''Copies files from source to destinatin if they don't already exist in destinatioj'''
    for hash, file_names in source_hashes.items():
        #If the hash for a file/s doesn´t exist at all in replica it copies all the files associated with that hash to replica
        if hash not in dest_hashes:
            for file_name in file_names:
                source_file_path = os.path.join(s_path, file_name)
                dest_file_path = os.path.join(d_path, file_name)

                if not os.path.exists(dest_file_path):
                    shutil.copy2(source_file_path, dest_file_path)
                    log_message =f"copied {source_file_path} to {dest_file_path}"
                    logging.info(log_message)
                    print(log_message)

        else:
            #If the hash already exists in replica( ex: in the case of existing 2 or more exact files with different names) it copies only the files that are not already in replica.
            dest_files = dest_hashes[hash]
            for file_name in file_names:
                if file_name not in dest_files:
                    source_file_path = os.path.join(s_path, file_name)
                    dest_file_path = os.path.join(d_path, file_name)
                    if not os.path.exists(dest_file_path):
                        shutil.copy2(source_file_path, dest_file_path)
                        log_message = f"copied {source_file_path} to {dest_file_path}"
                        logging.info(log_message)
                        print(log_message)


def remove_files(source_hashes, dest_hashes, s_path, d_path):
    '''Remove files from replica that are not present in source'''
    for hash, file_names in dest_hashes.items():
                if hash not in source_hashes:
                    #If the hash for a file/s doesn´t exist at all in source it removes all the files associated with that hash in replica:
                    for file_name in file_names:
                        remove_path = os.path.join(d_path, file_name)
                        if os.path.exists(remove_path):
                            os.remove(remove_path)
                            log_message =f"removed {remove_path}"
                            logging.info(log_message)
                            print(log_message)

                else:
                    #If the hash exists in source, it removes only the files from replica that are not in source:
                    #source_files = source_hashes[hash]
                    for file_name in file_names:
                        source_file_path = os.path.join(s_path, file_name)
                        remove_path = os.path.join(d_path, file_name)
                        if not os.path.exists(source_file_path):
                            if os.path.exists(remove_path):
                                os.remove(remove_path)
                                log_message= f"removed {remove_path}"
                                logging.info(log_message)
                                print(log_message)


def synch_directories(source, replica):


    #logging.info(f"Started: saving logs in {log_file}")

    if not os.path.exists(replica):
        os.makedirs(replica)
        logging.info(f"Created {replica}")
    
    if not os.path.exists(source):
        raise argparse.ArgumentError(None, "The source directory doesn't exist")

    source_hashes = {}
    source_sub_hashes = {}
    replica_hashes = {}
    replica_sub_hashes = {}
    s_sub_dir_files ={}
    r_sub_dir_files = {}

    dict_hashes(source, source_hashes, source_sub_hashes)
    dict_hashes(replica, replica_hashes, replica_sub_hashes)
    ls_dir(source, s_sub_dir_files)
    ls_dir(replica, r_sub_dir_files)

    create_remove_sub_folders(s_sub_dir_files, r_sub_dir_files, source, replica)
    copy_files(source_hashes, replica_hashes, source, replica)
    copy_files(source_sub_hashes, replica_sub_hashes, source, replica)
    remove_files(source_hashes, replica_hashes, source, replica)
    remove_files(source_sub_hashes, replica_sub_hashes, source, replica)


def main():
    parser = argparse.ArgumentParser(description= "Program to synch two directories, to stop it manually use keyboard interrupt 'CTRL+C':")
    parser.add_argument("--source", type=str, required=True, default="source", help="Replace SOURCE with the path to Source")
    parser.add_argument("--replica", type=str, required=True, default="replica", help="Replace REPLICA with the path to Replica")
    parser.add_argument("--log_file", type=str, required=True, default="log_file.txt", help="Replace LOG_FILE_PATH with Path to the Log File")
    parser.add_argument("--synch_interval", type=int, required=True, default=60, help="Replace SYNCH_INTERVAL with the time interval for synching in seconds")
    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file,format='%(asctime)s %(message)s',filemode='w', level=logging.INFO)
    logging.info(f"Started: saving logs in {args.log_file}")

    while True:
        try:
            synch_directories(args.source, args.replica)
            time.sleep(args.synch_interval)

        except KeyboardInterrupt:
            print("Program stopped by the user")
            raise SystemExit


if __name__ == "__main__":
    main()