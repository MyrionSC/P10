import os


def create_dirs(dirs):
    """
    :param dirs: a list of directories to create if these directories are not found
    :return: exit_code: 0=success -1=failed
    """
    try:
        for dir_ in dirs:
            if not os.path.exists(dir_):
                os.makedirs(dir_)
        return 0
    except Exception as err:
        print("Creating directories error: {0}".format(err))
        exit(-1)


def get_file_names_in_dir(dir_path):
    try:
        if os.path.exists(dir_path):
            return [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    except Exception as err:
        print("Getting file names in directory error: {0}".format(err))
        exit(-1)
