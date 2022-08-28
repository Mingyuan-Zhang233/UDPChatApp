Mingyuan Zhang	UNI: mz2715

**This program requires you to install Python 3.
**Verified Python version: 3.8, 3.9. Other versions may be able to run this program but normal functionality is not guarenteed.
**If Python 2 is not installed on your computer, you can replace all <python3> in the command with <python>



***********************************How to use UdpChat Server**********************************
**To start a UdpChat server, simply  type following command:                                                
python3 UdpChat.py -s <server-port>                                                                                      

**To terminate a running server, press Ctrl+C



***********************************How to use UdpChat Client************************************
**To start a UdpChat client, type the following command:
python3 UdpChat.py -c <your-name> <server-IP> <server-port> <client-port>

**To terminate a running client, press Ctrl+C or type exit

**You can type help to see all commands

**To send message to a user, type the following command
send <receiver-name> <your-message>

**To log out, type the following command
dereg <your-name>

**To log back in, type the following command
reg <your-name>

**To enter or exit debug mode, type debug


**Note: please make sure that UdpChat.py, Errors.py, and ChatApp.py are in the same directory.
**Note: all clients must be registered before they can function normally


**How does this program work
When UdpChat.py is called with correct argument, it instantiate a "server" object or "client" which extends "ChatApp", then invokes its operate() method.
**UDP communication:
Server: the server receive bytes from a blocking UDP socket and only take action when a bytes object arrives.
Client: the client receive bytes from a nonblocking UDP socket and take action when a bytes object arrives.
**UdpChat protocol:
Server and clients send and receive a bytes object which can be unpickled into a list object.
Upon reception of bytes from socket, the program first unpickle it into a list object called MSG.
MSG has two elements: MSG[0] is call msg_type which is a string indicating the type of this message.
MSG[1] is a list object called msg_list whose size is variable depending on msg_type.
The program executes corresponding method and process msg_list in a corresponding way, according to msg_type.
Any time when the program needs to send information, it construct a MSG list and pickle it into a bytes object.
When a corrupted message is received. The program simply discard it and take no action. 
**User input:
Server does not allow any user input once initiated. Server port is permenant and cannot be changed without terminating. 
Client can take a variety of input. 
Upon reception of a user input, the program executes corresponding function indicated by input.
If user gives input in incorrect format, corresponding error message will be displayed. 


**Data structure used
Majority of the data this program processes are lists. 
Client table is stored as an list of lists.
Offline chat is stored as an list of lists of tuples.
Sockets receive and send bytes, non-bytes objects are pickled before sending and unpickled after receiving. 

**Features
See PA1 materials for required features
Type help in program to see all functions


***********************************************************Test cases*********************************************************

##################################################################
Test-case 1(from handout):
*************************************Console of x ********************************************
Client process started.
You may type 'help' to see all commands.
[Welcome, You are registered.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> z: hi
>>> y: hi
>>> send y hi
[Message received by y.]
>>> send z hi
[Message received by z.]
>>> dereg x
Type 'stay' if you don't want to exit the program after de-registration: stay
[You are Offline. Bye.]
>>> reg x
[Welcome back, You are registered.]
[You have messages!]
y: 24-Nov-2020 (07:44:56) hi from y
z: 24-Nov-2020 (07:45:06) hi from z
>>> [Client table updated.]
>>> exit
Exit before de-registration is highly unrecommended.
If you want to proceed to exit, type 'YES': YES

*******************************************Console of y***************************************
Client process started.
You may type 'help' to see all commands.
[Welcome, You are registered.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> z: hi
>>> send x hi
[Message received by x.]
>>> send z hi
[Message received by z.]
>>> x: hi
>>> [Client table updated.]
>>> send x hi from y
[x is offline! Message received by the server and saved]
>>> [Client table updated.]
>>> exit
Exit before de-registration is highly unrecommended.
If you want to proceed to exit, type 'YES': YES


*******************************************Console of z***************************************
Client process started.
You may type 'help' to see all commands.
[Welcome, You are registered.]
>>> [Client table updated.]
>>> send x hi
[Message received by x.]
>>> send y hi
[Message received by y.]
>>> y: hi
>>> x: hi
>>> [Client table updated.]
>>> send x hi from z
[x is offline! Message received by the server and saved]
>>> [Client table updated.]
>>> exit
Exit before de-registration is highly unrecommended.
If you want to proceed to exit, type 'YES': YES

##########################################################################
Test-case 2(from handout):

*****************************************Console of x***************************************************
Client process started.
You may type 'help' to see all commands.
[Welcome, You are registered.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> send y hi
[y is offline! Server is not responding. ]
>>> dereg x
Type 'stay' if you don't want to exit the program after de-registration: exit
Cannot reach the server. Retrying...
Cannot reach the server. Retrying...
Cannot reach the server. Retrying...
Cannot reach the server. Retrying...
Cannot reach the server. Retrying...
[Server not responding]
Exiting...

**********************************************Console of y**************************************************
Client process started.
You may type 'help' to see all commands.
[Welcome, You are registered.]
>>> [Client table updated.]
>>> dereg y
Type 'stay' if you don't want to exit the program after de-registration: exit
[You are Offline. Bye.]
 Exiting...

########################################################################








