
from git import Repo
from git import Git
import os.path
import os, shutil
import time
from datetime import datetime

import re
import collections
from tqdm import tqdm

'''
There are two repositories rep1 and rep2. They are constantly under development and every now and then
the changes in rep1 should be merged into rep2. This script was created to automate some steps required to
complete this task.

The first high level method create_rep1_and_rep2_repo_files is going throuth all commits between specified dates,
makes list of files changed in these commits with the commits' dates. The results are then written to the two files.

The next method rep1_minus_and_intersection_rep2_files produces list of files changed in rep1 and not changed in rep2.
Changes in rep1 should be limited by dates e.g. of particular releases. The period of dates for rep2 should probably
cover the entire lifetime of rep2 project.The second list includes the files changed in both repos. The two lists are
stored in the file.

The last method copy_rep1_to_rep2_files copies files from the first list mentioned above from rep1 into rep2 locally with
some exceptions (let's say we do not want to copy database alter scripts as the are in rep1). The second list
unfortunately should be reviewed and merged manually.

The specified version of rep1 should be checked out and pulled locally.

'''

p = re.compile('[a-z]+')

join = os.path.join

# Repository rep1 working directory and limiting dates of changes
rep1_start_date = datetime.strptime('25-10-2019', '%d-%m-%Y')
rep1_end_date = datetime.strptime('13-02-2020 23:59', '%d-%m-%Y %H:%M')
rep1 = "{rep1_repo_working_directory}"

# Repository rep2 working directory and limiting dates of changes
rep2_start_date = datetime.strptime('21-10-2019', '%d-%m-%Y')
rep2_end_date = datetime.now()
rep2 = "{rep2_repo_working_directory}"

# Output files paths
rep1_files_out = '{path_to_folder}/rep1_files.txt'
rep2_files_out = '{path_to_folder}/rep2_files.txt'
rep1_minus_rep2_out = '{path_to_folder}/rep2_rep1_minus_rep2_out.txt'
rep1_intersection_rep2_out = '{path_to_folder}/rep1_intersection_rep2_out.txt'

def repo_files(repo_working_dir, start_date, end_date):
    repo = Repo(repo_working_dir)
    working_dir = repo.working_tree_dir
    files_dict = {}

    print ("working dir %s" % working_dir)

    g = Git(repo.working_dir)
    g.init()
    first_commits = list(repo.iter_commits())
    for item in tqdm(first_commits):

        if(datetime.fromtimestamp(item.committed_date) <= end_date):
            cdate = time.strftime("%a, %d %b %Y %H:%M", time.gmtime(item.committed_date))
            print("[%s], [%s]: %s" % (cdate, item.committer.name, item.message.strip()))
            if (datetime.fromtimestamp(item.committed_date) < start_date ): break

            changed_files = list(item.stats.files.keys())
            print(changed_files)

            for file_path in changed_files:
                if (files_dict.get(file_path, -1) < item.committed_date and item.committer.name != 'jenkins'):
                    files_dict[file_path] = item.committed_date

    # order by key
    files_ordered_dict = collections.OrderedDict(sorted(files_dict.items(), key=lambda t: t[0]))
    print_dict(files_ordered_dict)

    return files_ordered_dict


def print_dict(dict):
    print("####dict####")
    print(len(dict))
    for k, v in dict.items():
        print(str(k) + ' ' + str(v) + " {:%d-%b-%Y}".format(datetime.fromtimestamp(int(v))));

def printToFile(dict, out):
    with open(out, 'w', newline='') as out1:
        for k, v in dict.items():
            out1.write(str(k) + ' ' + str(v)+ '\n')
    return

def readDictFromFile(path):
    dict = collections.OrderedDict()
    with open(path, 'r', newline='') as f1:
        for line in f1:
            key = line.split(" ")[0].strip()
            value = line.split(" ")[1].strip()
            dict[key] = value
    return dict

# files to be copied from rep1 to rep2 without checking their content
# because there is no changes in the rep2 files from the beginning of rep2 development
def rep1_minus_rep2(rep1_dict, rep2_dict):
    dict = {}
    rep1_minus_rep2 = sorted(rep1_dict.keys() - rep2_dict.keys())
    for file_path in rep1_minus_rep2:
        dict[file_path] = rep1_dict[file_path]
    return dict

def rep1_intersection_rep2(rep1_dict, rep2_dict):
    dict = {}
    rep1_minus_rep2 = sorted(rep1_dict.keys() & rep2_dict.keys())
    for file_path in rep1_minus_rep2:
        dict[file_path] = rep1_dict[file_path]
    return dict

def copy_files(path_list, from_dir, to_dir):
    for path in path_list:
        from_path = os.path.join(from_dir, path)
        to_path = os.path.join(to_dir, path)
        shutil.copyfile(from_path, to_path)


####### high level methods #####

def create_rep1_and_rep2_repo_files():
    rep1_files = repo_files(rep1 ,rep1_start_date, rep1_end_date)
    printToFile(rep1_files, rep1_files_out)

    rep2_files = repo_files(rep2 ,rep2_start_date, rep2_end_date)
    printToFile(rep2_files, rep2_files_out)


def rep1_minus_and_intersection_rep2_files():
    rep1_dict = readDictFromFile(rep1_files_out)
    rep2_dict = readDictFromFile(rep2_files_out)
    rep1_minus_rep2_dict = rep1_minus_rep2(rep1_dict, rep2_dict)
    printToFile(rep1_minus_rep2_dict, rep1_minus_rep2_out)

    rep1_intersection_rep2_dict = rep1_intersection_rep2(rep1_dict, rep2_dict)
    printToFile(rep1_intersection_rep2_dict, rep1_intersection_rep2_out)

def copy_rep1_to_rep2_files():
    rep1_minus_rep2_dict = readDictFromFile(rep1_minus_rep2_out)
    rep1_minus_rep2_paths = rep1_minus_rep2_dict.keys()
    path_list = []
    for path in rep1_minus_rep2_paths:
        if not (path.startswith('{some_key_word}')):
            path_list.append(path)
    copy_files(path_list, rep1, rep2)
    return path_list

