""" Contains a utility function to double check that an
expected file type is being used"""

from enum import Enum

class FileFormat(str, Enum):
    """Enumeration for acceptable file formats"""
    FILE_TYPE_CSV = "csv"
    FILE_TYPE_CSV_INTERNAL = "internal"
    FILE_TYPE_HTML = "wa_html"

def verify_file_type(file_type):
    """file_type is something like CSV or .CSV, returns a file_type_ string
    if matched (and None if nothing matches)
    Supported file types: CSV, TXT (assumed to be CSV), HTML or WA_HTML"""

    # just in case someone specifies 'CSV' instead of csv, etc:
    file_type = file_type.translate(None, '\'". ').lower()

    #print "\tVerifyType without dot:"+ file_type+"<<<"

    if file_type == 'csv' or \
       file_type == 'txt':
        #print '\tFound "csv"'
        return FileFormat.FILE_TYPE_CSV
    elif file_type == 'html' or \
         file_type == 'wa_html':
        #print "\tFound 'HTML'"
        return FileFormat.FILE_TYPE_HTML
    else:
        return None
