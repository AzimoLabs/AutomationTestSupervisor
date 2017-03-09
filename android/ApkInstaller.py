import time
from functools import partial
from threading import Thread

from console.ShellHelper import *

apk_dir = "app-automation-integrationTest.apk"

devices = ["emulator-5554", "emulator-5556", "emulator-5558"]


def install(device_name):
    start_time = int(round(time.time() * 1000))
    print('[{:%H:%M:%S}]: '.format(datetime.datetime.now())
          + "Installation started on device '" + device_name + "'.")

    install_cmd = "bin -s " + device_name + " install " + apk_dir + " &"
    #execute_shell(install_cmd)

    end_time = int(round(time.time() * 1000))
    print('[{:%H:%M:%S}]: '.format(datetime.datetime.now())
          + "Installation ended on device '" + device_name + "'. It took: " + str(
        (end_time - start_time) / 1000) + " seconds.")


if __name__ == '__main__':
    for device in devices:
        Thread(target=partial(install, device)).start()
