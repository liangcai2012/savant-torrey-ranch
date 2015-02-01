1. THe project uses python libary rpyc. You need to install that package to run the tests. The project run ok on linux and windows.
2The project includes 4 test cases. see comments in testcase.py for detail.

3. The defaule settings is the server and client running on the same machine.Update the variable [host] in cli.py to the server IP address if  the server and client are running on different machines.

4 run server.py first, then run cli.py

5. You can run run-svr.sh and run-cli.sh if your system is linux.

6. The directroy [xml] include my test code for xmlrpc. The code is not wrapped up.

7 The directory [socket] includes my test code for TCP/socket.The code is not wrapped up.

8 On my system. Test case 3 report the transfter speed of about 100MByte/second.Test case 4 report the transfter speed of about 4MByte/second.