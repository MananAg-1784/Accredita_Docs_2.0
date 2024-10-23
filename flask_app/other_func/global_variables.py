
from json import loads
from flask_app.database import connection
from datetime import datetime
import pytz

class User:
    def __init__(self, id, privilage = None, dept = None, logged_in = False):
        self.id = id
        self.service = None
        self.logged_in = logged_in
        self.privilage = privilage
        self.dept = dept
        self.dept_id = None
        self.sid = None
        self.uploading_files = []

    def login_user(self):
        self.logged_in = True

    def logout_user(self):
        self.logged_in = False

class FileData:
    def __init__(self, sid, total_size, name):
        self.sid = sid
        self.file_data = b''    # None as soon as data is read
        self.total_size = total_size
        self.name = name
        self.read_size = 0
        self.Lock = True
        self.acc = None
        self.fields = None

class FileDataDetails:
    def __init__(self, sid, **kwargs):
        self.sid = sid
        self.uploadingLock = 0
        self.itemNo = kwargs.get('itemNo')
        self.categories = kwargs.get('categories')
        self.name = kwargs.get('name')
        self.size = kwargs.get('size')
        self.mimeType = kwargs.get('mimeType')
        self.segment = kwargs.get('segment')
        self.desc = kwargs.get('desc')
        self.extraSegment = {}

# user_id : User()
users = {}

# privilages are their id's
accreditions = [ x['accredition'] for x in connection.execute_query('select accredition from accreditions') ]

priv = {'admin': ['search', 'upload', 'update'], 'viewer' : ['search'], 'editor' : ['search', 'upload']}

def date_now(typeStr=False, onlyDate = True):
    intz = pytz.timezone('Asia/Kolkata')
    format_ = "%Y-%m-%d %H:%M:%S.%f"
    if onlyDate:
        format_ = "%Y-%m-%d"

    nowdt = datetime.now(intz).strftime(format_)
    if typeStr:
        return nowdt

    nowdt = datetime.strptime(nowdt, format_)
    return nowdt
