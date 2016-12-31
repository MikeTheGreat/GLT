"""Contains a class definition for Student"""
import os.path
from glt.Constants import EnvOptions

_NOTFOUND = object()

class Student(object):
    """Student objects contain a first and last name and email"""

    def __init__(self, f_name=None, l_name=None, email=None, glid=-1, **kwargs):
        """constructor.  Given first name, last name, and email address.
        email may be empty"""
        self.email = email
        if not kwargs:
            self.first_name = f_name
            self.last_name = l_name
            self.glid = glid
        else:
            self.glid = kwargs.get('id')
            username = kwargs.get('username')
            self.first_name, self.last_name = self.get_real_name(username)

    def __str__(self):
        """converts to string, in the format "Last, First, Email, GitLab-ID"""
        # Note that self.email may be empty.  This is ok - it'll make deserializing it easier.
        return self.last_name + ", " + self.first_name + ", " \
            + str(self.email) + ", " + str(self.glid)

    def __repr__(self):
        """Converts to string, just like __str__"""
        return self.__str__()

    def __eq__(self, other):
        """ Comparison method.  If GitLab IDs are present on both
        objects and they match then the objects are the same.
        Otherwise check the first/last names and email for matches
        Shamelessly copied from http://stackoverflow.com/questions/3550336/comparing-two-objects"""

        val1, val2 = [getattr(obj, 'glid', _NOTFOUND) for obj in [self, other]]
        # if both present and they match
        if val1 is _NOTFOUND or val2 is _NOTFOUND:
            return False
        if val1 != -1 and val2 != -1 and val1 == val2:
            return True

        for attr in ['first_name', 'last_name', 'email']:
            val1, val2 = [getattr(obj, attr, _NOTFOUND) for obj in [self, other]]
            if val1 is _NOTFOUND or val2 is _NOTFOUND:
                return False
            elif val1 != val2:
                return False
        return True

    def get_user_name(self):
        """Gets a username suitable for use in GitLab.  
        Currently it's <first name>_<last name>"""
        return self.first_name+"_"+self.last_name

    def get_group_name(self):
        """Gets a name for a group, in order to create a group
        containing just this student"""
        return self.get_user_name() + "_GROUP"

    def get_real_name(self, username):
        """Given a username (Currently it's <first name>_<last name>),
        return first_name, last_name"""
        return username.split('_')

    def get_dir_name(self):
        """Get a directory name suitable for saving homework in.
        Currently it's:
            self.last_name + ", " + self.first_name"""
        return self.last_name + ", " + self.first_name

    def generate_hw_dir(self, env, project_name):
        """Get a directory name for a particular hw project, based
        on the pattern in env[EnvOptions.HW_LOC]"""
        if EnvOptions.HW_LOC not in env:
            raise Exception("student.generate_hw_dir: EnvOptions.HW_LOC not present in env!")
        
        pattern = env[EnvOptions.HW_LOC]

        pattern = pattern.replace('SECTION_NAME', env[EnvOptions.SECTION])
        pattern = pattern.replace('ASSIGNMENT', project_name)
        pattern = pattern.replace('NAME_LAST', self.last_name)
        pattern = pattern.replace('NAME_FIRST',self.first_name)

        base_path = env[EnvOptions.STUDENT_WORK_DIR]

        #pattern = str(pattern)
        #base_path = str(base_path)

        student_dest_dir = os.path.join(base_path,
            pattern)

        return student_dest_dir
    