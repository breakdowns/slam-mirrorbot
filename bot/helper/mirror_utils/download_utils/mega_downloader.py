from bot import LOGGER, MEGA_API_KEY, download_dict_lock, download_dict, MEGA_EMAIL_ID, MEGA_PASSWORD
import threading
from mega import (MegaApi, MegaListener, MegaRequest, MegaTransfer, MegaError)
from bot.helper.telegram_helper.message_utils import *
import os
from bot.helper.ext_utils.bot_utils import new_thread, get_mega_link_type, get_readable_file_size
from bot.helper.mirror_utils.status_utils.mega_download_status import MegaDownloadStatus
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot import MEGA_LIMIT, STOP_DUPLICATE, TAR_UNZIP_LIMIT
import random
import string

class MegaDownloaderException(Exception):
    pass


class MegaAppListener(MegaListener):
    _NO_EVENT_ON = (MegaRequest.TYPE_LOGIN,MegaRequest.TYPE_FETCH_NODES)
    NO_ERROR = "no error"

    def __init__(self, continue_event: threading.Event, listener):
        self.continue_event = continue_event
        self.node = None
        self.public_node = None
        self.listener = listener
        self.uid = listener.uid
        self.__bytes_transferred = 0
        self.is_cancelled = False
        self.__speed = 0
        self.__name = ''
        self.__size = 0
        self.error = None
        self.gid = ""
        super(MegaAppListener, self).__init__()

    @property
    def speed(self):
        """Returns speed of the download in bytes/second"""
        return self.__speed

    @property
    def name(self):
        """Returns name of the download"""
        return self.__name

    def setValues(self, name, size, gid):
        self.__name = name
        self.__size = size
        self.gid = gid

    @property
    def size(self):
        """Size of download in bytes"""
        return self.__size

    @property
    def downloaded_bytes(self):
        return self.__bytes_transferred

    def onRequestStart(self, api, request):
        pass

    def onRequestFinish(self, api, request, error):
        if str(error).lower() != "no error":
            self.error = error.copy()
            return
        request_type = request.getType()
        if request_type == MegaRequest.TYPE_LOGIN:
            api.fetchNodes()
        elif request_type == MegaRequest.TYPE_GET_PUBLIC_NODE:
            self.public_node = request.getPublicMegaNode()
        elif request_type == MegaRequest.TYPE_FETCH_NODES:
            LOGGER.info("Fetching Root Node.")
            self.node = api.getRootNode()
            LOGGER.info(f"Node Name: {self.node.getName()}")
        if request_type not in self._NO_EVENT_ON or self.node and "cloud drive" not in self.node.getName().lower():
            self.continue_event.set()

    def onRequestTemporaryError(self, api, request, error: MegaError):
        LOGGER.info(f'Mega Request error in {error}')
        if not self.is_cancelled:
            self.listener.onDownloadError("RequestTempError: " + error.toString())
            self.is_cancelled = True
        self.error = error.toString()
        self.continue_event.set()

    def onTransferStart(self, api: MegaApi, transfer: MegaTransfer):
        pass

    def onTransferUpdate(self, api: MegaApi, transfer: MegaTransfer):
        if self.is_cancelled:
            api.cancelTransfer(transfer, None)
        self.__speed = transfer.getSpeed()
        self.__bytes_transferred = transfer.getTransferredBytes()

    def onTransferFinish(self, api: MegaApi, transfer: MegaTransfer, error):
        try:
            if transfer.isFolderTransfer() and transfer.isFinished() or transfer.getFileName() == self.name and not self.is_cancelled:
                self.listener.onDownloadComplete()
                self.continue_event.set()
        except Exception as e:
            LOGGER.error(e)

    def onTransferTemporaryError(self, api, transfer, error):
        filen = transfer.getFileName()
        state = transfer.getState()
        errStr = error.toString()
        LOGGER.info(f'Mega download error in file {transfer} {filen}: {error}')

        if state == 1 or state == 4:
            # Sometimes MEGA (offical client) can't stream a node either and raises a temp failed error.
            # Don't break the transfer queue if transfer's in queued (1) or retrying (4) state [causes seg fault]
            return

        self.error = errStr
        if not self.is_cancelled:
            self.is_cancelled = True
            self.listener.onDownloadError(f"TransferTempError: {errStr} ({filen})")

    def cancel_download(self):
        self.is_cancelled = True
        self.listener.onDownloadError("Download Canceled by user")


class AsyncExecutor:

    def __init__(self):
        self.continue_event = threading.Event()

    def do(self, function, args):
        self.continue_event.clear()
        function(*args)
        self.continue_event.wait()

listeners = []

class MegaDownloadHelper:
    def __init__(self):
        pass

    @staticmethod
    @new_thread
    def add_download(mega_link: str, path: str, listener):
        if MEGA_API_KEY is None:
            raise MegaDownloaderException('Mega API KEY not provided! Cannot mirror Mega links')
        executor = AsyncExecutor()
        api = MegaApi(MEGA_API_KEY, None, None, 'telegram-mirror-bot')
        global listeners
        mega_listener = MegaAppListener(executor.continue_event, listener)
        listeners.append(mega_listener)
        api.addListener(mega_listener)
        if MEGA_EMAIL_ID is not None and MEGA_PASSWORD is not None:
            executor.do(api.login, (MEGA_EMAIL_ID, MEGA_PASSWORD))
        link_type = get_mega_link_type(mega_link)
        if link_type == "file":
            LOGGER.info("File. If your download didn't start, then check your link if it's available to download")
            executor.do(api.getPublicNode, (mega_link,))
            node = mega_listener.public_node
        else:
            LOGGER.info("Folder. If your download didn't start, then check your link if it's available to download")
            folder_api = MegaApi(MEGA_API_KEY,None,None,'TgBot')
            folder_api.addListener(mega_listener)
            executor.do(folder_api.loginToFolder, (mega_link,))
            node = folder_api.authorizeNode(mega_listener.node)
        if mega_listener.error is not None:
            return listener.onDownloadError(str(mega_listener.error))
        if STOP_DUPLICATE:
            LOGGER.info(f'Checking File/Folder if already in Drive')
            mname = node.getName()
            if listener.isTar:
                mname = mname + ".tar"
            if listener.extract:
                smsg = None
            else:
                gd = GoogleDriveHelper()
                smsg, button = gd.drive_list(mname)
            if smsg:
                msg1 = "File/Folder is already available in Drive.\nHere are the search results:"
                sendMarkup(msg1, listener.bot, listener.update, button)
                return
        if MEGA_LIMIT is not None or TAR_UNZIP_LIMIT is not None:
            limit = None
            LOGGER.info(f'Checking File/Folder Size')
            if TAR_UNZIP_LIMIT is not None and (listener.isTar or listener.extract):
                limit = TAR_UNZIP_LIMIT
                msg3 = f'Failed, Tar/Unzip limit is {TAR_UNZIP_LIMIT}.\nYour File/Folder size is {get_readable_file_size(api.getSize(node))}.'
            elif MEGA_LIMIT is not None and limit is None:
                limit = MEGA_LIMIT
                msg3 = f'Failed, Mega limit is {MEGA_LIMIT}.\nYour File/Folder size is {get_readable_file_size(api.getSize(node))}.'
            if limit is not None:
                limit = limit.split(' ', maxsplit=1)
                limitint = int(limit[0])
                if 'G' in limit[1] or 'g' in limit[1]:
                    if api.getSize(node) > limitint * 1024**3:
                        sendMessage(msg3, listener.bot, listener.update)
                        return
                elif 'T' in limit[1] or 't' in limit[1]:
                    if api.getSize(node) > limitint * 1024**4:
                        sendMessage(msg3, listener.bot, listener.update)
                        return
        with download_dict_lock:
            download_dict[listener.uid] = MegaDownloadStatus(mega_listener, listener)
        os.makedirs(path)
        gid = ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=8))
        mega_listener.setValues(node.getName(), api.getSize(node), gid)
        sendStatusMessage(listener.update, listener.bot)
        executor.do(api.startDownload,(node,path))
