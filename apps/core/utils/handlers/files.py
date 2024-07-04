import os


def delete_files(files):
    """
    Remove temporary files used to import e merge track files

    :param files: List of tracks
    :return: None
    """

    for file in files:
        os.remove(file)
