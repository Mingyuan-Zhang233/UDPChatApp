import socket
import pickle
import select
import sys
import Errors
import datetime


# ChatApp sends and receives standardized message in list form:
# [boolean: message type, list: msg]
class ChatApp:
    # boolean
    server_mode = None  # server indicator
    state = None  # activity indicator
    # String
    name = None
    ip = None
    hostname = None
    # int
    port = None
    # socket
    sock = None
    # list: [str, tuple, boolean]
    clients_table = None      # [[name],[(address, port)],[status]]

    def __init__(self, nm, pt):
        self.name = nm
        self.port = pt
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.clients_table = [[], [], []]
        self.state = True

    # receive from socket, return a tuple of (message, source address)
    def receive(self, buffer_size=2048):
        msg_byte, source_address = self.sock.recvfrom(buffer_size)
        msg = pickle.loads(msg_byte)
        return msg, source_address

    # send msg to address
    def send(self, msg, address):
        msg_byte = pickle.dumps(msg)
        self.sock.sendto(msg_byte, address)

    # find index of client by name return -1 if name not in client table
    def indexOfClient(self, nm):
        try:
            idx = self.clients_table[0].index(nm)
        except ValueError:
            idx = -1
        return idx

    # find index of client by address return -1 if address not in client table
    def indexOfAddress(self, addr):
        try:
            idx = self.clients_table[1].index(addr)
        except ValueError:
            idx = -1
        return idx

    # get client name by index
    def getClientByIndex(self, idx):
        nm = None
        try:
            nm = self.clients_table[0][idx]
        except IndexError:
            print("Index out of bound.\n")
        return nm

    # print table
    def debug_printTable(self):
        for idx in range(0, len(self.clients_table[0])):
            line = (self.clients_table[0][idx], self.clients_table[1][idx], self.clients_table[2][idx])
            print(line)




class server(ChatApp):

    # [[(time, sender name, message)]] idx = receiver index
    saved_chat = None

    def __init__(self, nm, pt):
        self.saved_chat = []
        ChatApp.__init__(self, nm, pt)
        print("Server successfully initiated")
        print('Server IP: ' + str(self.ip) + '    Port: ' + str(self.port))

    def operate(self):
        while True:
            # blocking, only operates when receiving something
            received_msg, source_address = self.receive()
            msg_type = received_msg[0]
            msg = received_msg[1]
            # registration
            if msg_type == 'reg':
                client_name = msg[0]
                idx = self.indexOfClient(client_name)
                # check if  the client is returning user
                if idx >= 0:
                    # check if the name is used by other user
                    if self.clients_table[2][idx]:
                        respond = ['reg-f', ["Nickname '$$' is taken by another user!".replace('$$', client_name)]]
                        self.send(respond, source_address)
                    # register the returning client
                    else:
                        saved_msg = []
                        saved_msg_num = len(self.saved_chat[idx])
                        for saved_chat_tuple in self.saved_chat[idx]:
                            temp_msg = saved_chat_tuple[1] + ": " + saved_chat_tuple[0] + " " + saved_chat_tuple[2]
                            saved_msg.append(temp_msg)
                        self.saved_chat[idx] = []
                        self.setAddress(idx, source_address)
                        self.setOnline(idx)
                        respond = ['reg-s', ['[Welcome back, You are registered.]', saved_msg], self.clients_table]
                        self.send(respond, source_address)
                        self.updateTable()
                else:
                    self.addClient(client_name, source_address)
                    respond = ['reg-s', ['[Welcome, You are registered.]', []], self.clients_table]
                    self.send(respond, source_address)
                    self.updateTable()
            elif msg_type == 'dereg':
                idx = -1
                response_type = 'dereg-f'
                response_msg = ['Unknown error.']
                try:
                    idx = self.clients_table[0].index(msg[0])
                    self.clients_table[2][idx] = False
                    self.updateTable()
                    response_type = 'dereg-s'
                    self.send([response_type, response_msg], source_address)
                except ValueError:
                    response_type = 'dereg-f'
                    response_msg = ['You are not registered.']
                    self.send([response_type, response_msg], source_address)
                except:
                    self.send([response_type, response_msg], source_address)
            elif msg_type == 'text':
                sender_name = msg[0]
                receiver_name = msg[1]
                text = msg[2]
                receiver_idx = self.indexOfClient(receiver_name)
                # save if receiver offline
                if not self.clients_table[2][receiver_idx]:
                    respond_type = 'text-s'
                    respond_msg = ['Success']
                    # get a timestamp
                    timestamp = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
                    self.saved_chat[receiver_idx].append((timestamp, sender_name, text))
                    self.send([respond_type, respond_msg], source_address)
                # verify
                else:
                    if self.verifyClientStatus(receiver_idx):
                        respond_type = 'text-f'
                        respond_msg = ['User is online']
                        self.send([respond_type, respond_msg])
                    else:
                        respond_type = 'text-s'
                        respond_msg = ['Success']
                        # get a timestamp
                        timestamp = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
                        self.saved_chat[receiver_idx].append((timestamp, sender_name, text))
                        self.setOffline(receiver_idx)
                        self.send([respond_type, respond_msg], source_address)
                        self.updateTable()

    # push the updated table to all known client
    def updateTable(self):
        # construct broadcast message
        msg_type = 'update'
        msg = self.clients_table
        for idx in range(0, len(self.clients_table[0])):
            if self.clients_table[2][idx]:
                self.send([msg_type, msg], self.clients_table[1][idx])

    # set client address by index
    def setAddress(self, idx, addr):
        try:
            self.clients_table[1][idx] = addr
        except IndexError:
            print('Index out of bound. \n')

    # set client online by index
    def setOnline(self, idx):
        try:
            self.clients_table[2][idx] = True
        except IndexError:
            print('Index out of bound. \n')

    # set client offline by index
    def setOffline(self, idx):
        try:
            self.clients_table[2][idx] = False
        except IndexError:
            print('Index out of bound. \n')

    # add clietn to table
    def addClient(self, nm, addr, status=True):
        self.clients_table[0].append(nm)
        self.clients_table[1].append(addr)
        self.clients_table[2].append(status)
        self.saved_chat.append([])

    def verifyClientStatus(self, idx):
        result = False
        self.send(['verify', []], self.clients_table[1][idx])
        self.sock.settimeout(0.5)
        try:
            msg, addr = self.receive()
            if msg[0] == 'verify' and msg[1][0] == self.getClientByIndex(idx):
                result = True
            else:
                result =False
        except socket.timeout:
            result =False
        self.sock.settimeout(None)
        return result

    # check if a client has offline chat, if user DNE return -1
    def checkSavedChat(self, receiver_idx):
        result = -1
        try:
            result = len(self.saved_chat[receiver_idx])
        except IndexError:
            print(Errors.user_DNE)
        return result




class client(ChatApp):
    # int
    server_port = None
    retry_times = 1
    # String
    server_ip = None
    # float
    client_timeout = 0.5  # default timeout is 500ms
    # boolean
    debug_mode = False
    registered = False

    def __init__(self, nm, s_ip, s_port, c_port):
        ChatApp.__init__(self, nm, c_port)
        self.server_ip = s_ip
        self.debug_mode = False
        self.registered = False
        self.server_port = s_port
        print("Client process started. \nYou may type 'help' to see all commands.")
        self.register()

    def operate(self):
        user_input = None
        received_msg = None
        source_address = None
        msg_type = None
        msg = None
        while True:
            sock_lst, wr, er = select.select([self.sock], [], [], 0.0001)
            input_lst, wr, er = select.select([sys.stdin], [], [],0.0001)
            msg_here = len(sock_lst) > 0
            input_here = len(input_lst) > 0
            # self.sock.settimeout(0)
            # try:
            #     received_msg, source_address = self.receive()
            #     msg_here = True
            # except socket.timeout:
            #     received_msg = ['None', []]
            #     source_address = (None, None)
            #     msg_here = False
            # self.sock.settimeout(None)
            if input_here:
                user_input = sys.stdin.readline()
                user_input = user_input.strip().split(' ', 2)
            else:
                user_input = [None, None]
            msg_type = None
            msg = None
            source_address = None
            if msg_here:
                received_msg, source_address = self.receive()
                try:
                    msg_type = received_msg[0]
                    msg = received_msg[1]
                except TypeError:
                    print(Errors.unknown_message)
                    self.prompt()
                    msg_here = False
            else:
                received_msg = [None, []]
                source_address = (None, None)
            if self.debug_mode:
                print('There is message: ', msg_here)
                print('There is input: ', input_here)
                if msg_here:
                    print('Msg type: ',msg_type)
            # execute user's input
            if input_here:
                input_type = user_input[0]
                if not Errors.checkUserInput(input_type, user_input):
                    print(Errors.invalid_user_input)
                    self.prompt()
                else:
                    if input_type == 'set':
                        time_out = input("Set default timeout to: ").strip()
                        retry = input("Set how many times you try to reach a client before sending to server: ").strip()
                        self.setClientTimeout(time_out)
                        self.setRetry(retry)
                        print('Parameters successfully set!')
                        self.prompt()
                    elif input_type == 'show':
                        print("Client IP: " + self.ip)
                        print('Client Port: ' + str(self.port))
                        print('Your Name: ' + self.name)
                        if self.registered:
                            print('Registration status: Online')
                        else:
                            print('Registration status: Offline')
                        self.prompt()
                    # the following codes work fine but should be re-structured
                    if self.registered:
                        # registration
                        if input_type == 'reg':
                            print(Errors.multiple_logon.replace('$$', user_input[1]))
                            self.prompt()
                        # de-registration
                        elif input_type == 'dereg':
                            if user_input[1] == self.name:
                                self.de_register()
                            else:
                                print(Errors.invalid_dereg)
                                self.prompt()
                        # sending message
                        elif input_type == 'send':
                            text = user_input[2]
                            receiver_name = user_input[1]
                            rvalid = receiver_name != self.name
                            if not rvalid:
                                print("You can't sent message to yourself!")
                                self.prompt()
                            receiver_idx = self.indexOfClient(receiver_name)
                            # check if the receiving client exist in client table
                            if receiver_idx < 0:
                                print(Errors.user_DNE)
                                self.prompt()
                            # send if client exist
                            else:
                                if self.debug_mode:
                                    print("Executing send method.")
                                if rvalid:
                                    self.sendMessage(text, receiver_name, receiver_idx)
                        elif input_type == 'debug':
                            # toggle debug mode indicator
                            self.debug_mode = not self.debug_mode
                            # print current table
                            if self.debug_mode:
                                print("DEBUG mode activated.")
                            else:
                                print("Exiting DEBUG mode.")
                            if self.debug_mode:
                                print('This client is registered: ' + str(self.registered))
                                print("IP: " + self.ip)
                                print('Port: ' + str(self.port))
                                print('Name: ' + self.name)
                                print('Current client table is: ')
                                self.debug_printTable()
                                self.prompt()
                        elif input_type == 'help':
                            print(Errors.help_message)
                            self.prompt()
                        # exiting program
                        elif input_type == 'exit':
                            print("Exit before de-registration is highly unrecommended.")
                            print("Exiting without de-registration may block you from logging back into the Client.")
                            if input("If you want to proceed to exit, type 'YES': ").strip() == "YES":
                                sys.exit()
                            else:
                                print("Process resumed.")
                                self.prompt()
                    else:
                        if input_type == 'reg':
                            self.name = user_input[1]
                            self.register()
                        elif input_type == 'debug':
                            # toggle debug mode indicator
                            self.debug_mode = not self.debug_mode
                            # print current table
                            if self.debug_mode:
                                print("DEBUG mode activated.")
                            else:
                                print("Exiting DEBUG mode.")
                            if self.debug_mode:
                                print('This client is registered: '+str(self.registered))
                                print("IP: "+self.ip)
                                print('Port: '+str(self.port))
                                print('Name: '+self.name)
                                print('Current client table is: ')
                                self.debug_printTable()
                                self.prompt()
                        elif input_type == 'help':
                            print(Errors.help_message)
                            self.prompt()
                        # exiting program
                        elif input_type == 'exit':
                            print("Exit before de-registration is highly unrecommended.")
                            if input("Do you really want to exit? (yes/no): ").strip() == "yes":
                                sys.exit()
                            else:
                                print("Process resumed.")
                                self.prompt()
                        else:
                            print(Errors.unregistered_user)
                            self.prompt()

            # present and respond received message
            if msg_here:
                if msg_type == 'update':
                    if isinstance(msg, list) and isinstance(msg[0], list):
                        self.clients_table = msg
                        print('[Client table updated.]')
                        self.prompt()
                    else:
                        print(Errors.corrupted_clients_table)
                        print("The previous client table is kept.")
                        self.prompt()
                elif msg_type == 'verify':
                    if self.debug_mode:
                        print('Status verified by server!')
                    self.send(['verify', [self.name]], source_address)
                elif msg_type == 'text':
                    # send ACK when received message
                    self.send(['text-s', []], source_address)
                    if self.debug_mode:
                        print("ACK sent")
                    # display the received message
                    sender_name = msg[0]
                    text = msg[2]
                    disp = sender_name + ": " + text
                    print(disp)
                    self.prompt()

    # register this client to server
    def register(self):
        # loop until an available name is provide by the user
        self.sock.settimeout(1.0)
        while True:
            # construct a registration msg
            msg_type = 'reg'
            client_info = [self.name]
            self.send([msg_type, client_info], (self.server_ip, self.server_port))
            try:
                response, source_address = self.receive()
                # make sure the respond comes from the server.
                if source_address == (self.server_ip, self.server_port):
                    if response[0] == 'reg-s':
                        self.registered = True
                        print(response[1][0])
                        if len(response[1][1]) > 0:
                            print("[You have messages!]")
                            for saved_chat in response[1][1]:
                                print(saved_chat)
                        self.prompt()
                        self.clients_table = response[2]
                        break
                    elif response[0] == 'reg-f':
                        print(response[1][0])
                        self.name = input('Please enter another nickname: ').strip().split()[0]
                    else:
                        print(Errors.invalid_registration_response)
                        print("To register, type 'reg <nick-name>'.")
                        self.prompt()
                        break
            except TypeError:
                print(Errors.unknown_message)
                print("To register, type 'reg <nick-name>'.")
                self.prompt()
                break
            except socket.timeout:
                print(Errors.server_not_responding+' Please try again later!')
                print("To register, type 'reg <nick-name>'.")
                self.prompt()
                break
        self.sock.settimeout(None)

    # de-register
    def de_register(self):
        exit_tag = input("Type 'exit' if you want to exit the program after de-registration: ").strip() == 'exit'
        msg_type = 'dereg'
        msg = [self.name, (self.ip, self.port)]
        self.sock.settimeout(0.5)
        response = None
        for it in range(0,5):
            self.send([msg_type, msg], (self.server_ip, self.server_port))
            try:
                response, source_address = self.receive()
            except socket.timeout:
                print('Server not responding. Retrying...')
                response = ['None',[]]
            if response[0] == 'dereg-s':
                self.registered = False
                if exit_tag:
                    print("[You are Offline. Bye.] \n Exiting...")
                    sys.exit()
                else:
                    print("[You are Offline. Bye.]")
                    self.prompt()
                    self.sock.settimeout(None)
                    return
            elif response[0] == 'dereg-f':
                if exit_tag:
                    print("De-registration Failed.")
                    print(response[1][0])
                    print('Exiting...')
                    sys.exit()
                else:
                    print("De-registration Failed.")
                    print(response[1][0])
                    self.prompt()
                    self.sock.settimeout(None)
                    return
        self.sock.settimeout(None)
        print("[The server is offline.]")
        if exit_tag:
            print("Exiting...")
            sys.exit()
        else:
            self.prompt()

    # send 'text' to receiver
    def sendMessage(self, text, receiver_name, receiver_idx):
        sending_msg_type = 'text'
        sending_msg = [self.name, receiver_name, text]
        if self.debug_mode:
            print('Receiver status: ', self.clients_table[2][receiver_idx])
        # check if the receiver is online
        if self.clients_table[2][receiver_idx]:
            self.sock.settimeout(self.client_timeout)
            temp_ctr = 0
            temp_tag = 0
            # make 5 attempt stop if either client or server responds
            while temp_ctr < self.retry_times:
                successfully_sent = False
                sent_to_server = False
                if self.debug_mode:
                    print('Attempt number: ' + str(temp_ctr))
                try:
                    self.send([sending_msg_type, sending_msg], self.clients_table[1][receiver_idx])
                    response, response_address = self.receive()
                    if self.debug_mode:
                        print("ACK(client): ", response, response_address)
                        print("Address bool: ", response_address == self.clients_table[1][receiver_idx], "Type bool: ", response[0] == 'text-s')
                    if response[0] == 'text-s':
                        successfully_sent = True
                        temp_ctr = self.retry_times
                # contact the server only when client is not responding
                except socket.timeout:
                    self.sock.settimeout(self.client_timeout*3)
                    print("[No ACK from $$, sending message to server.]".replace("$$", receiver_name))
                    try:
                        self.send([sending_msg_type, sending_msg], (self.server_ip, self.server_port))
                        response, response_address = self.receive()
                        if self.debug_mode:
                            print("ACK(server): ", response, response_address)
                            print("Address bool: ", response_address == (self.server_ip, self.server_port), "Type bool: ", response[0] == 'text-s')
                        if response[0] == 'text-s':
                            sent_to_server = True
                            temp_ctr = self.retry_times
                    except socket.timeout:
                        sent_to_server = False
                    self.sock.settimeout(self.client_timeout)
                temp_ctr += 1
                if successfully_sent:
                    temp_tag = 1
                elif sent_to_server:
                    temp_tag = 2
                else:
                    temp_tag = 3
            self.sock.settimeout(None)
            if temp_tag == 1:
                print("[Message received by $$.]".replace("$$", receiver_name))
                self.prompt()
            elif temp_tag == 2:
                print("[Messages received by the server and saved]")
                self.prompt()
            elif temp_tag == 3:
                print("[Client unreachable and Server not responding.]")
                print("[If you want to exit the program, type 'exit'.]")
                self.prompt()
        # send to the server if client is offline
        else:
            # wait longer since the server may need to verify
            self.sock.settimeout(self.client_timeout*3)
            server_timeout = False
            sent_to_server = False
            try:
                self.send([sending_msg_type, sending_msg], (self.server_ip, self.server_port))
                response, response_address = self.receive()
                if response[0] == 'text-s':
                    sent_to_server = True
                elif response[0] == 'text-f':
                    sent_to_server = False
            except socket.timeout:
                server_timeout = True
            self.sock.settimeout(None)
            if sent_to_server:
                print("[$$ is offline! Message received by the server and saved]".replace('$$', receiver_name))
                self.prompt()
            elif server_timeout:
                print("[$$ is offline! Server is not responding. ]".replace('$$', receiver_name))
                self.prompt()
            else:
                print("""[$$ is offline! Your message will be sent to the server and saved.]
$$ is still online! Updating your local client table!""")
                self.prompt()

    # set timeout (in second)
    def setClientTimeout(self, to):
        try:
            self.client_timeout = float(to)
        except:
            print("Timeout must be a float number.")
            self.prompt()

    def setRetry(self, num):
        try:
            self.retry_times = int(num)
        except:
            print("Retry times must be a integer.")
            self.prompt()

    # display prompt
    def prompt(self):
        print('', end='>>> ', flush=True)