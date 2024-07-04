import shutil


def delete_directory(directory):
    """
    Remove temporary files used to import e merge track files

    :param directory: directory that will be deleted
    :return: None
    """

    shutil.rmtree(directory)

