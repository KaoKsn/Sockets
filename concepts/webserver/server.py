import socket, sys

DEFAULT_PORT = 8080
CRLF = "\r\n\r\n"
msg = "Hola, soy el server!"

def main():
    port = DEFAULT_PORT
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    bind_addr = ("0.0.0.0", port)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(bind_addr)

    s.listen(5)
    print(f"Server listening on port {port}..")
    while True:
        c, addr = s.accept()
        request = []
        while True:
            chunk = c.recv(4096)
            if not chunk:
                break
            request.append(chunk.decode())

            if CRLF in "".join(request):
                break
        request = "".join(request)

        request_headers = request.split("\r\n")
        if len(request_headers) >= 1:
            print(addr, request_headers[0].split(" ")[0])
        else:
            print(addr, "")
        if CRLF not in request:
            response = (
                "HTTP/1.1 400 Bad Request\r\n"
                f"Connection: close{CRLF}"
            )
        else:
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{msg}"
            )
        c.sendall(response.encode())
        c.close()
    s.close()
main()
