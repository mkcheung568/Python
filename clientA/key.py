from Crypto import Random
from Crypto.PublicKey import RSA
 
 
random_generator = Random.new().read
rsa = RSA.generate(2048, random_generator)
# Private Key
private_key = rsa.exportKey()
print(private_key.decode('utf-8'))
# Public Key
public_key = rsa.publickey().exportKey()
print(public_key.decode('utf-8'))

with open('rsa_private_key.pem', 'wb')as f:
    f.write(private_key)
    
with open('rsa_public_key.pem', 'wb')as f:
    f.write(public_key)
