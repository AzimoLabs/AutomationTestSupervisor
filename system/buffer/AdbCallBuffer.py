import time
import threading

from settings import GlobalConfig

_adb_call_buffer = list()


def is_adb_cmd(cmd):
    adb_bin_found = False

    cmd_parts = cmd.split(" ")
    if cmd_parts:
        bin_part = cmd_parts[0]

        if bin_part is not None and len(bin_part) >= 3:
            last_three_letters = bin_part[-3:]
            adb_bin_found = last_three_letters.lower() == "adb"
    return adb_bin_found


def report_adb_call():
    if _is_full():
        _wait_for_empty_slot()
    _report_adb_call()


def _is_full():
    return len(_adb_call_buffer) >= GlobalConfig.ADB_CALL_BUFFER_SIZE


def _wait_for_empty_slot():
    while True:
        if not _is_full():
            break
        time.sleep(0.1)


def _report_adb_call():
    cmd_call_time = int(round(time.time() * 1000))
    _adb_call_buffer.append(cmd_call_time)

    remove_slot_thread = _ReleaseBufferSlotThread(_adb_call_buffer, cmd_call_time)
    remove_slot_thread.start()


class _ReleaseBufferSlotThread(threading.Thread):
    TAG = "_ReleaseBufferSlotThread"

    def __init__(self, buffer, cmd_call_time):
        super().__init__()

        self.buffer = buffer
        self.cmd_call_time = cmd_call_time

    def run(self):
        while (self._get_current_time_millis() - self.cmd_call_time) < GlobalConfig.ADB_CALL_BUFFER_DELAY_BETWEEN_CMD:
            time.sleep(0.1)
        self.buffer.remove(self.cmd_call_time)

    @staticmethod
    def _get_current_time_millis():
        return int(round(time.time() * 1000))
