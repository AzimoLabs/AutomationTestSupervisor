from error.Exceptions import LauncherFlowInterruptedException

from system.bin.SystemShellCommands import GeneralCommand
from system.console import (
    ShellHelper,
    Printer
)

TAG = "PortManager:"


def get_open_ports(avd_set):
    _check_port_rules(avd_set)

    ports_to_use = avd_set.avd_port_rules.ports_to_use
    if len(ports_to_use) > 0:
        message = "Requested ports:"
        for port in ports_to_use:
            message += (" '" + str(port) + "'")
        message += "."
        message(TAG, message)

    ports_to_ignore = avd_set.avd_port_rules.ports_to_ignore
    if len(ports_to_ignore) > 0:
        message = "Ignoring ports:"
        for port in ports_to_ignore:
            message += (" '" + str(port) + "'")
        message += "."
        Printer.system_message(TAG, message)

    should_assign_missing_ports = avd_set.avd_port_rules.assign_missing_ports
    if should_assign_missing_ports:
        Printer.system_message(TAG, "Not requested ports will be automatically assigned.")
    else:
        Printer.system_message(TAG, "Port auto assignment is turned off. Only specified ports will be used.")

    avd_instances = 0
    for avd in avd_set.avd_list:
        avd_instances += avd.instances

    range_min = avd_set.avd_port_rules.search_range_min
    range_max = avd_set.avd_port_rules.search_range_max
    Printer.system_message(TAG, "Checking for " + str(avd_instances) + " open ports in range <" + str(
        range_min) + ", " + str(range_max) + ">.")

    available_ports = list()

    for port in ports_to_use:
        try:
            ShellHelper.execute_shell(GeneralCommand.CHECK_PORT.format(port), False, False)
            port_open = False
        except:
            port_open = True

        if port_open:
            available_ports.append(port)
        else:
            message = "Port {} was requested but is currently used."
            message = message.format(str(port))
            raise LauncherFlowInterruptedException(TAG, message)

    if should_assign_missing_ports:
        temp_port = range_min
        for i in range(avd_instances - len(available_ports)):
            while temp_port < range_max and len(available_ports) != avd_instances:
                try:
                    ShellHelper.execute_shell(GeneralCommand.CHECK_PORT.format(temp_port), False, False)
                    port_open = False
                except:
                    port_open = True

                if port_open:
                    if temp_port not in available_ports and temp_port not in ports_to_ignore:
                        available_ports.append(temp_port)
                else:
                    Printer.error(TAG, "Port " + str(temp_port) + " is currently used and will be omitted.")

                temp_port += 2

        if len(available_ports) != avd_instances:
            message = "There are only {} open ports available in range <{}, {}>. Requested amount: {}."
            message = message.format(str(len(available_ports)), str(range_min), str(range_max), str(avd_instances))
            raise LauncherFlowInterruptedException(TAG, message)

    return available_ports


def _check_port_rules(avd_set):
    avd_instances = 0
    avd_rules = avd_set.avd_port_rules

    for avd in avd_set.avd_list:
        avd_instances += avd.instances

    if len(avd_rules.ports_to_use) != len(set(avd_rules.ports_to_use)):
        message = "'Ports to use' list contains duplicates."
        raise LauncherFlowInterruptedException(TAG, message)

    if len(avd_rules.ports_to_ignore) != len(set(avd_rules.ports_to_ignore)):
        message = "'Ports to ignore' list contains duplicates."
        raise LauncherFlowInterruptedException(TAG, message)

    for port_to_be_used in avd_rules.ports_to_use:
        if port_to_be_used % 2 == 1:
            message = "Port numbers has to be even."
            raise LauncherFlowInterruptedException(TAG, message)

    for port_to_be_used in avd_rules.ports_to_use:
        if port_to_be_used < avd_rules.search_range_min or port_to_be_used > avd_rules.search_range_max:
            message = "Requested to use port {} is out of range <{}, {}>."
            message = message.format(str(port_to_be_used), str(avd_rules.search_range_min),
                                     str(avd_rules.search_range_max))
            raise LauncherFlowInterruptedException(TAG, message)

    for port_to_be_ignored in avd_rules.ports_to_ignore:
        for port_to_be_used in avd_rules.ports_to_use:
            if port_to_be_used == port_to_be_ignored:
                message = "Port {} is set to be used and ignored at the same time."
                message = message.format(str(port_to_be_used))
                raise LauncherFlowInterruptedException(TAG, message)

    if not avd_rules.assign_missing_ports:
        requested_ports_to_use_num = len(avd_rules.ports_to_use)
        if requested_ports_to_use_num != avd_instances:
            message = ("There are {} AVD instances about to be created according to set, but there were only {} ports "
                       "requested to use. Set 'assign_missing_ports' to True or add more ports to list.")
            message = message.format(str(avd_instances), str(requested_ports_to_use_num))
            raise LauncherFlowInterruptedException(TAG, message)
