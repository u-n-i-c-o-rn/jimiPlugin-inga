import time

from core import db, audit

# Initialize
dbCollectionName = "inga"

class _inga(db._document):
    scanName = str()
    ip = str()
    up = bool()
    lastScan = int()
    history = list()

    _dbCollection = db.db[dbCollectionName]

    def new(self, scanName, ip, up):
        self.scanName = scanName
        self.name = ip
        self.ip = ip
        self.up = up
        return super(_inga, self).new()

    def updateRecord(self, ip, up):
        audit._audit().add("inga","history",{ "lastUpdate" : self.lastUpdateTime, "endDate" : int(time.time()), "ip" : self.ip, "up" : self.up })
        self.lastScan = int(time.time())
        self.ip = ip
        self.up = up
        self.update(["lastScan","ip","up"])