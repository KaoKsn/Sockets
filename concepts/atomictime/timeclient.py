import socket, time, sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("time.nist.gov", 37))  # Time protocol.

s.settimeout(5)

data = b""
try:
    while len(data) < 4:
        chunk = s.recv(4 - len(data))
        if not chunk:
            raise RuntimeError("Server closed before sending 4 bytes")
        data += chunk

    # seconds since 1900 Jan 1
    # big endian bytes format(network time format).
    data = int.from_bytes(data, "big")

except Exception as e:
    print(e, file=sys.stderr)

timedelta = 2208988800
system = int(time.time()) + timedelta

print("NIST", data)
print("System:", system)

s.close()
