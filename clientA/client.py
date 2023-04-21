# client import
import socket, threading, time, sys
from datetime import datetime
# crypto import
import base64
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher

# This is ClientA
nickname = "Client A"

#connecting to  server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPv4, SOCK_STREAM = TCP protocol 
client.connect(('192.168.8.113', 8085))  # loopback address, port

#listening to server and sending nickname
def receive():
    try:
        while True:
            #receive message from client
            #if 'Nick' send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            # > 200 is means check the cipher text or signature is longer than 200 char
            elif len(message) > 200:
                #print(message)
                if(rsa_public_check_sign1(readMessage(),message)):
                    if(checkWhichClient(readMessage(),"A")):           
                        print("Client B Message : " + decrypt_data(readMessage(),"A"))
                    elif(checkWhichClient(readMessage(),"B")):
                        print("Client A Message : " + decrypt_data(readMessage(),"B"))
                    else:
                        print("decrypt fail")
                elif(rsa_public_check_sign2(readMessage(),message)):
                    if(checkWhichClient(readMessage(),"A")):           
                        print("Client B Message : " + decrypt_data(readMessage(),"A"))
                    elif(checkWhichClient(readMessage(),"B")):
                        print("Client A Message : " + decrypt_data(readMessage(),"B"))
                    else:
                        print("decrypt fail")
                else:
                    print("signature fail")
            # else is print the time and the client name
            else:
                print(message)
    except:
        print('[Receive] An error occured')
        client.close()

#sending message to server
def write():
    try:
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            message_title = '[{0}] [{1}] '.format(current_time,nickname)
            encrypt_user_message =encrypt_data(input(''))
            signed_message = rsa_private_sign(encrypt_user_message)
            #print("encrypt_user_message : " + encrypt_user_message)
            #print("signed_message : " + signed_message)

            writeMessage(encrypt_user_message)
            print("") # create a waiting gap,the code run more stable
            client.send(message_title.encode('ascii'))
            print("") # create a waiting gap,the code run more stable
            client.send(signed_message.encode('ascii'))
    except:
        print('[Input] An error occured')
        client.close()
        sys.exit()  

# get the key value
def get_key(key_file):
    with open(key_file) as f:
        data = f.read()
        key = RSA.importKey(data)
    return key

def writeMessage(message):
    with open('../message.text', 'w')as f:
        f.write(message)

def readMessage():
    with open('../message.text', 'r')as f:
        data = f.read()
    return data

# encrypt the message
def encrypt_data(message):
    public_key = get_key('../rsa_public_key_B.pem')  
    cipher = PKCS1_cipher.new(public_key)
    encrypt_text = base64.b64encode(cipher.encrypt(bytes(message.encode("utf-8"))))
    return encrypt_text.decode('utf-8')

# decrypt the message
def decrypt_data(encrypt_message,userType):
    private_key = get_key('../rsa_private_key_{}.pem'.format(userType))
    cipher = PKCS1_cipher.new(private_key)
    back_text = cipher.decrypt(base64.b64decode(encrypt_message), 0)
    return back_text.decode('utf-8')

# sign the encrypt message
def rsa_private_sign(data):
    private_key = get_key('rsa_private_key_A.pem')
    signer = PKCS1_signature.new(private_key)
    digest = SHA.new()
    digest.update(data.encode("utf8"))
    sign = signer.sign(digest)
    signature = base64.b64encode(sign)
    signature = signature.decode('utf-8')
    return signature

# check the signature is correct
def rsa_public_check_sign1(text, sign):
    publick_key = get_key('../rsa_public_key_A.pem')
    verifier = PKCS1_signature.new(publick_key)
    digest = SHA.new()
    digest.update(text.encode("utf8"))
    return verifier.verify(digest, base64.b64decode(sign))

def rsa_public_check_sign2(text, sign):
    publick_key = get_key('../rsa_public_key_B.pem')
    verifier = PKCS1_signature.new(publick_key)
    digest = SHA.new()
    digest.update(text.encode("utf8"))
    return verifier.verify(digest, base64.b64decode(sign))

# check this message is who send
def checkWhichClient(encrypt_message,userType):
    return decrypt_data(encrypt_message,userType)

#starting threads for listening and sending
receive_thread = threading.Thread(target=receive) 
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
         