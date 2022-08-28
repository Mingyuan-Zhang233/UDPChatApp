from ChatApp import *
import Errors
import sys

# [String]
initArgs = sys.argv[1:]
# boolean
server_mode = None
# int
server_port = None
client_port = None
server_ip = None
# String
name = 'server'  # default name is server


# loop until the user enter all arguments in valid forms
while True:
    # check number of arguments
    if len(initArgs) == 2:
        # check mode selection
        if initArgs[0] == '-s':
            if not Errors.isInteger(initArgs[1]):
                print(Errors.incorrect_server_port)
                initArgs[1] = input('Please re-enter port number: ').strip()
            else:
                port_arg = int(initArgs[1])
                # check if given port is valid
                if not Errors.portIsValid(port_arg):
                    print(Errors.port_number_invalid)
                    initArgs[1] = input('Please re-enter port number: ').strip()
                elif not Errors.portIsAvailable(port_arg):
                    print(Errors.port_unavailable)
                    initArgs[1] = input('Please enter another port number: ').strip()
                else:
                    server_port = port_arg
                    server_mode =True
                    break
        else:
            print(Errors.incorrect_argument)
            initArgs = input('Please re-enter arguments: ').strip().split()

    elif len(initArgs) == 5:
        # check mode selection
        if initArgs[0] == '-c':
            client_args = initArgs[1:]  # client_args = [name, server_ip, server_port, client_port]
            client_args_type = Errors.checkClientArguments(client_args)
            if not client_args_type[0]:
                initArgs[1] = input('Please re-enter client name: ').strip().split()[0]
            elif not client_args_type[1]:
                print(Errors.invalid_server_IP)
                initArgs[2] = input('Please enter a valid IP: ').strip()
            elif not client_args_type[2]:
                print(Errors.incorrect_server_port)
                initArgs[3] = input('Please enter a valid server port number: ').strip()
            elif not client_args_type[3]:
                print(Errors.incorrect_client_port)
                initArgs[4] = input('Please enter a valid client port number: ').strip()
            else:
                if not Errors.portIsAvailable(int(client_args[3])):
                    print(Errors.port_unavailable)
                    initArgs[4] = input('Please enter another client port number: ').strip()
                elif client_args[0].strip() == 'server':
                    initArgs[1] = input("Name 'server' is reserved for the server! \n Please enter another name: ").strip().split()[0]
                else:
                    server_mode = False
                    server_ip = client_args[1]
                    name = client_args[0]
                    server_port = int(client_args[2])
                    client_port = int(client_args[3])
                    break
        else:
            print(Errors.incorrect_argument)
            initArgs = input('Please re-enter arguments: ').strip().split()
    else:
        print(Errors.incorrect_argument)
        initArgs = input('Please re-enter arguments: ').strip().split()
# initiate client or server according to user's choice
if server_mode:
    server_process = server(name,server_port)
    server_process.operate()
else:
    client_process = client(name,server_ip, server_port,client_port)
    client_process.operate()