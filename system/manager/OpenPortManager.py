from console.ShellHelper import *
from console.Printer import *
from system.command.GeneralCommand import *

TAG = "OpenPortProvider:"


def get_open_ports(avd_set):
    _check_port_rules(avd_set)

    ports_to_use = avd_set.avd_port_rules.ports_to_use
    if len(ports_to_use) > 0:
        message = "Requested ports for AVD:"
        for port in ports_to_use:
            message += (" '" + str(port) + "'")
        message += "."
        print_message(TAG, message)

    ports_to_ignore = avd_set.avd_port_rules.ports_to_ignore
    if len(ports_to_ignore) > 0:
        message = "Ignoring ports:"
        for port in ports_to_ignore:
            message += (" '" + str(port) + "'")
        message += "."
        print_message(TAG, message)

    ports_auto_assign = avd_set.avd_port_rules.assign_missing_ports
    if ports_auto_assign:
        print_message(TAG, "Not requested ports will be automatically assigned.")
    else:
        print_message(TAG, "Port auto assignment is turned off. Only specified ports will be used.")

    avd_instances = 0
    for avd in avd_set.avd_list:
        avd_instances += avd.instances

    range_min = avd_set.avd_port_rules.search_range_min
    range_max = avd_set.avd_port_rules.search_range_max
    print_message(TAG,
                  "Checking for " + str(avd_instances) + " open ports in range <" + str(range_min) + ", "
                  + str(range_max) + ">.")

    available_ports = list()

    for port in ports_to_use:
        try:
            execute_shell(GeneralCommand.CHECK_PORT.format(port), False, False)
            port_open = False
        except:
            port_open = True

        if port_open:
            available_ports.append(port)
        else:
            print_error(TAG, "Port " + str(port) + " was requested but is currently used.")
            quit()

    if ports_auto_assign:
        temp_port = range_min
        for i in range(avd_instances - len(available_ports)):
            while temp_port < range_max and len(available_ports) != avd_instances:
                try:
                    execute_shell(GeneralCommand.CHECK_PORT.format(temp_port), False, False)
                    port_open = False
                except:
                    port_open = True

                if port_open:
                    if temp_port not in available_ports and temp_port not in ports_to_ignore:
                        available_ports.append(temp_port)
                else:
                    print_error(TAG, "Port " + str(temp_port) + " is currently used and will be omitted.")

                temp_port += 2

        if len(available_ports) != avd_instances:
            print_error(TAG, "There are only " + str(len(available_ports)) + " open ports available in range <"
                        + str(range_min) + ", " + str(range_max) + ">. Requested amount: " + str(avd_instances) +
                        ".")
            quit()

    return available_ports


def _check_port_rules(avd_set):
    avd_instances = 0
    avd_rules = avd_set.avd_port_rules

    for avd in avd_set.avd_list:
        avd_instances += avd.instances

    if len(avd_rules.ports_to_use) != len(set(avd_rules.ports_to_use)):
        print_error(TAG, "'Ports to use' list contains duplicates.")
        quit()

    if len(avd_rules.ports_to_ignore) != len(set(avd_rules.ports_to_ignore)):
        print_error(TAG, "'Ports to ignore' list contains duplicates.")
        quit()

    for port_to_be_used in avd_rules.ports_to_use:
        if port_to_be_used % 2 == 1:
            print_error(TAG, "Port numbers has to be even")
            quit()

    for port_to_be_used in avd_rules.ports_to_use:
        if port_to_be_used < avd_rules.search_range_min or port_to_be_used > avd_rules.search_range_max:
            print_error(TAG, "Requested to use port " + str(port_to_be_used) + " is out of range " +
                        "<" + str(avd_rules.search_range_min) + ", " + str(avd_rules.search_range_max) + ">.")
            quit()

    for port_to_be_ignored in avd_rules.ports_to_ignore:
        for port_to_be_used in avd_rules.ports_to_use:
            if port_to_be_used == port_to_be_ignored:
                print_error(TAG,
                            "Port " + str(port_to_be_used) + " is set to be used and ignored at the same time.")
                quit()

    if not avd_rules.assign_missing_ports:
        requested_ports_to_use_num = len(avd_rules.ports_to_use)
        if requested_ports_to_use_num != avd_instances:
            print_error(TAG, "There are " + str(
                avd_instances) + " AVD instances about to be created according to set, but there were only " +
                        str(requested_ports_to_use_num) + " ports requested to use. Set \"assign_missing_ports\"" +
                        " to True or add more ports to list.")
            quit()
