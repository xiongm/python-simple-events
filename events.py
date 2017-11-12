from event_base import EventBase

"""
Add all new events definition here
"""


class FileNotification(EventBase):
    def __init__(self, inputPath=None, recvMtime=None):
        super().__init__(inputPath, recvMtime)
        self.inputPath = inputPath
        self.recvMtime = recvMtime


class AckComplete(EventBase):
    def __init__(self, encryptedDataPath=None, feedbackPath=None, encryptedMetaPath=None):
        super().__init__(encryptedDataPath, feedbackPath, encryptedMetaPath)
        self.encryptedDataPath = encryptedDataPath
        self.feedbackPath = feedbackPath
        self.encryptedMetaPath = encryptedMetaPath


class IntegrityComplete(EventBase):
    def __init__(self, dataPath=None, feedbackPath=None, fileID=None, origFileID=None, isKindDone=False):
        super().__init__(dataPath, feedbackPath, fileID, origFileID, isKindDone)
        self.dataPath = dataPath
        self.feedbackPath = feedbackPath
        self.fileID = fileID
        self.origFileID = origFileID
        self.isKindDone = isKindDone


class OrderingComplete(EventBase):
    def __init__(self, dataPath=None, feedbackPath=None):
        super().__init__(dataPath, feedbackPath)
        self.dataPath = dataPath
        self.feedbackPath = feedbackPath


class IngestionComplete(EventBase):
    def __init__(self, feedbackPath=None, dumpPath=None, configPath=None, failurePath=None, isSuccess=True):
        super().__init__(feedbackPath, dumpPath, configPath, failurePath, isSuccess)
        self.feedbackPath = feedbackPath
        self.dumpPath = dumpPath
        self.configPath = configPath
        self.failurePath = failurePath
        self.isSuccess = isSuccess


class RefdataComplete(EventBase):
    def __init__(self, feedbackPath=None):
        super().__init__(feedbackPath)
        self.feedbackPath = feedbackPath


class FeedbackEncryptionComplete(EventBase):
    def __init__(self, encryptedPath=None, relativeSubPath=None, completeFilePath=None):
        super().__init__(encryptedPath, relativeSubPath, completeFilePath)
        self.encryptedPath = encryptedPath
        self.relativeSubPath = relativeSubPath
        self.completeFilePath = completeFilePath
