from virginia import *

# plain = "hello world!"
plain = "This is a book. That is a cat. I am a boy. One of my boy go to school today."
# plain = "This is a book"
key = [0,2,4]
etext = encrypt(plain, key)
dtext = decrypt(etext, key)
print('etext=', etext)
print('dtext=', dtext)
print('fit(plain)=', fit(plain))