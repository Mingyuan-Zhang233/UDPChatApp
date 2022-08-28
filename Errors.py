# This file manage all error messages and error checkers

import socket


# All checkers for potential errors are managed here

# check if client parameters are applicable types
# return a list of booleans: [is_str, is_int, is_int, is_int]
def checkClientArguments(arg_list):
    result = [False, False, False, False]
    result[0] = isinstance(arg_list[0], str)
    result[1] = checkIsIP(arg_list[1])
    result[2] = portIsValid(arg_list[2])
    result[3] = portIsValid(arg_list[3])
    return result


# check if ip_str is a string literal for IP
def checkIsIP(ip_str):
    ip = ip_str.split('.')
    result = len(ip) == 4
    for str_num in ip:
        str_num = str_num.strip()
        if not isInteger(str_num):
            result = False
        else:
            result = result and 0 <= int(str_num) <= 255
    return result

# check if the user enter input in correct syntax
def checkUserInput(input_type, user_input):
    type_result = False
    input_result = False
    if input_type == 'send':
        type_result = True
        input_result = len(user_input) == 3
    elif input_type == 'reg':
        type_result = True
        input_result = len(user_input) == 2
    elif input_type == 'dereg':
        type_result = True
        input_result = len(user_input) == 2
    elif input_type == 'exit' or input_type == 'debug' or input_type == 'set':
        type_result = True
        input_result = len(user_input) == 1
    elif input_type == 'help' or input_type == 'show':
        type_result = True
        input_result = len(user_input) == 1
    return type_result and input_result

# check if it is a int literal
def isInteger(str_num):
    try:
        num = int(str_num)
    except:
        return False
    else:
        return True


# check if a port is available
def portIsAvailable(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("0.0.0.0", port))
        result = True
    except:
        result = False
    finally:
        sock.close()
    return result


# check if a port number or port number str literal is valid
def portIsValid(port):
    if isinstance(port,int):
        return 65535 >= port >= 1024
    elif isinstance(port,str):
        if isInteger(port):
            return 65535 >= int(port) >= 1024
        else:
            return False
    else:
        return False


# All error messages are managed here

corrupted_clients_table = """A client table update is received, but it is corrupted."""

help_message = """List of all commands:
dereg <your-name>:          de-register
send <name> <message>:      send <message> to <name>.
reg <nick-name>:            register as <nick-name>.
help:                       display help message.
show                        show local user information.

Following commands are for not recommended for users:
exit:                       exit without de-registration.
set:                        setting default parameters.
debug:                      enter or exit DEBUG mode."""

incorrect_argument = """Arguments incorrect!
To initialize UdpChat, please use arguments in the following formats:
UdpChat -s <port>
UdpChat -c <nick-name> <server-ip> <server-port> <client-port> """

incorrect_client_port = """Client port is incorrect!
Port number must be an integer in 1024-65535 (including bounds)."""

invalid_dereg = """You cannot force other users offline!
You may only de-register yourself!"""

incorrect_server_port = """Server port is incorrect!
Port number must be an integer in 1024-65535 (including bounds)."""

invalid_IP = """The IP address is invalid!
IP address must be 4 integers in 0-255 (including bounds) separated by '.'"""

invalid_registration_response = """The registration respond is corrupted"""

invalid_server_IP = """The server IP address is invalid!
IP address must be 4 integers in 0-255 (including bounds) separated by '.'"""

invalid_user_input = """The command is invalid.
Please enter command in the following format: 
dereg <nick-name>
send <name> <message>
reg <nick-name>
[You may type help to view all commands.]"""

multiple_logon = """A client can only logon to one account.
To regiser as $$, please de-register the current client."""

port_number_invalid = """Port number is invalid!
Port number must be in 1024-65535 (including bounds)."""

port_unavailable = """The port you choose is unavailable!"""

server_not_responding = """Server not responding."""

unknown_message = """A received message cannot be interpreted.
It may be corrupted, or in the wrong format"""

unknown = """An unknown error occurred.
Please restart the program."""

unregistered_user = """You are not registered, you must register first!"""

user_DNE = """The user to whom you try to send message does not exist!"""


