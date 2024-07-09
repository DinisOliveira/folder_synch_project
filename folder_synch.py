import os
import hashlib
import shutil


def calculate_hash(file_path):
    '''Calculate MD5 hash of the file'''
    md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        '''Reading the file in chunks to not overload memory in case there are big files'''
        while chunck := file.read(8192):
            md5.update(chunck)
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
        '''Using os.listdir() in case there are no subdirectories since it's less process intensive because it only lists through the current directory''' 
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            update_hash_dict(file_path, filename, hash_dict_main)
        elif os.path.isdir(file_path):
            '''Using os.walk() in case there are subdirectories to be able to transverse the the directory and it's subdirectories''' 
            for dir, _, files in os.walk(file_path):
                for sub_file in files:
                    sub_file_path = os.path.join(dir, sub_file)
                    rel_sub_path_file = os.path.relpath(sub_file_path, path)
                    update_hash_dict(sub_file_path, rel_sub_path_file, hash_dict_sub)

def ls_dir(path, sub_dir_files):
    '''Lists directories and files, associating each directory name with their relative file paths'''
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


pathh = r"D:\\veeam\\Task\\source"
source_hashes = {}
source_sub_hashes = {}
s_sub_dir_files ={}

dict_hashes(pathh, source_hashes, source_sub_hashes)
ls_dir(pathh, s_sub_dir_files)
print(s_sub_dir_files)