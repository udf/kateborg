import json
from threading import Lock
import logging

class Katestore:
    """A stupid kv database, just like me"""
    def __init__(self, name, default_func, autosave=True):
        self.logger = logging.getLogger("Katestore@{}".format(name))
        self.name = name
        self.write_lock = Lock()
        self.default_func = default_func
        self.autosave = autosave
        try:
            with open(self.name) as f:
                self.dict = json.load(f)
            self.logger.info('Successfully loaded file!')
        except FileNotFoundError:
            self.dict = {}
            self.logger.info('Creating new file')
        
    def __getitem__(self, key):
        key = str(key)
        if key not in self.dict:
            return self.default_func()
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[str(key)] = value
        if self.autosave:
            self.save()

    def __contains__(self, key):
        return str(key) in self.dict

    def __delitem__(self, key):
        del self.dict[str(key)]
        if self.autosave:
            self.save()

    def save(self):
        with self.write_lock:
            with open(self.name, 'w') as f:
                json.dump(self.dict, f)