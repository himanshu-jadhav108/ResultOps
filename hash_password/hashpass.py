import hashlib

print(hashlib.sha256("read@1234".encode()).hexdigest())
print("-" * 30)
print(hashlib.sha256("write@1234".encode()).hexdigest())
