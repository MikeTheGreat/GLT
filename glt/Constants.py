"""File contains constants (like EnvOptions)"""

from enum import Enum

class EnvOptions(str, Enum):
    """This lists the keys for the rcfile and command line arguments.
    Note that this is a 'mix-in' enum, which means that saying
    EnvOptions.INFILE automatically uses the str() value for that member
    (i.e., EnvOptions.INFILE is "infile", without needing a .value on
    the .INFILE"""
    ACTION = "action" # Key used to store which command-line option (addStudents, etc) was chosen

    # common options:
    SERVER = 'server'
    SERVER_IP_ADDR = 'server_ip'
    USERNAME = 'username'
    PASSWORD = 'password'

    # command line args for creating student accounts
    CREATE_STUDENTS = "addStudents"
    INFILE = "infile"
    INFILE_TYPE = "infile_type"
    SECTION = "section"

    DELETE_CLASS = "deleteClass"

    # command line option for listing projects
    LIST_PROJECTS = "listProjects"

    NEW_HOMEWORK = "addHomework"
    HOMEWORK_NAME = 'homework_name'
    HOMEWORK_DIR = 'homework_path'

    # .gltrc file
    KNOWN_GOOD_ACCOUNTS = "known_good_accounts"
    DATA_DIR = "data_dir"
    TEMP_DIR = "temp_dir"