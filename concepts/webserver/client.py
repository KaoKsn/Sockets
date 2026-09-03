import socket, sys

DEFAULT_SERVICE_PORT = 80
DEFAULT_SERVICE = "127.0.0.1"

def main():
    service, port = DEFAULT_SERVICE, DEFAULT_SERVICE_PORT
    msg = ''

    if len(sys.argv) >= 2:
        service = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])
    if len(sys.argv) >= 4:
        msg = " ".join(sys.argv[3:])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server = (service, port)
    s.connect(server)

    request = (
        "GET / HTTP/1.1\r\n"
        f"Host: {service}\r\n"
        "Content-Type: text/plain;  charset=utf-8\r\n"
        f"Content-Length: {len(msg)}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{msg}"
    )
    s.sendall(request.encode())
    response = []
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        response.append(chunk.decode())
    response = "".join(response)
    print(response)

    s.close()

main()
