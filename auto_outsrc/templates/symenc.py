from toolbox.pairinggroup import *

group = PairingGroup(MNT160)

#R = group.random(GT)
Rstr = b"3:MjA6Z+Jw6hcPR40MRNKKrA4FV8ztPDwyMDpmf6K/0CrHw4UQst1iYq9QFB7woDIwOiunSkccLEXajoQFyGtZGcSjGNVkMjA6gzTplMwMwpbCsDdURVNxWj1UbWUyMDptgzr4zmIPwYDgcRrNg3lqlLLbqzIwOkAsvloI9I6glmnaQScHX0+tCsry"
R = group.deserialize(Rstr)
print("R := ", R)
key = hash(R)
print("aes key := ", key)
#key = b"123456789012345"
message = b"hello world12345"

c = SymEnc(key, message)
print("C := ", c)

m = SymDec(key, c)

print("m :=", m)

assert m == message, "invalid decryption!"
print("Successful Decryption!")
