"""
A simple webserver that listens to requests on port 80
and returns html/text/css/js/jp(e)*g/png/md files *only
"""

import socket
import threading
import os, sys
import time

import responses, configuration

HEADER_END = "\r\n\r\n"


def handler(c, addr, rootdir):
    request = []
    while True:
        try:
            chunk = c.recv(4096)
            if not chunk:
                break
            request.append(chunk.decode())
            if HEADER_END in "".join(request):
                break
        except Exception as e:
            print(e, file=sys.stderr)

    request = "".join(request)
    request_headers = request.split("\r\n")

    response, payload = None, str()
    formats = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "text/javascript",
        ".txt": "text/plain",
        ".md": "text/plain",
        ".pdf": "text/markdown",
        ".jpg": "image/jpg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }
    if request_headers:
        request_line = request_headers[0].strip()
        try:
            method, path, protocol = request_line.split(" ")
        except (ValueError, Exception) as e:
            response = responses.badrequest
        else:
            """
            Sanitize path.
                Avoid path traversal, symlink enabled path traversal.
                Use a local webserver root.
            """
            file = None
            server_root = os.path.realpath(rootdir)
            requested_path = os.path.realpath(os.path.sep.join((server_root, path)))
            print(requested_path)
            if not (
                requested_path == server_root
                or requested_path.startswith(server_root + os.sep)
            ):
                print(f"Request forbidden: {requested_path}", file=sys.stderr)
                response = responses.forbidden
            elif requested_path == server_root:
                file = requested_path + os.sep + "index.html"
            else:
                file = requested_path

            if not file:
                file = "./content"
            if os.path.isfile(file):
                if method in ["GET", "POST"] and protocol == "HTTP/1.1":
                    extension = os.path.splitext(file)[1].lower()
                    if extension not in formats.keys():
                        print(f"Unsupported extension: {extension}", file=sys.stderr)
                        response = responses.notfound
                    else:
                        try:
                            with open(file, "rb") as f:
                                payload = f.read().decode("iso-8859-1")
                                content_length = len(payload)
                            last_modified = time.ctime(os.path.getmtime(file))
                        except Exception as e:
                            print(e, file=sys.stderr)
                            response = responses.notfound
                        else:
                            if not last_modified:
                                last_modified = time.ctime()
                            response = (
                                "HTTP/1.1 200 OK\r\n"
                                f"Content-Type: {formats[extension]}; charset: iso-8859-1\r\n"
                                f"Content-Length: {content_length}\r\n"
                                f"Last-Modified: {last_modified}\r\n"
                                "Connection: close\r\n"
                                "\r\n"
                                f"{payload}"
                            )
            else:
                try:
                    dir_contents = os.listdir(file)
                    for file in dir_contents:
                        payload = payload + file + "\n"
                    content_length = len(payload)
                    extension = "txt"
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        f"Content-Type: text/{extension}; charset: iso-8859-1\r\n"
                        f"Content-Length: {content_length}\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                        f"{payload}"
                    )
                except Exception as e:
                    print(e, file=sys.stderr)
                    response = responses.notfound
        if response:
            try:
                c.sendall(response.encode("iso-8859-1"))
            except Exception as e:
                print(e, file=sys.stderr)
    c.close()


def main():
    try:
        server_config = configuration.init_config()
    except ValueError:
        return 1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_at = (server_config.bind_addr, server_config.port)

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(listen_at)

    print(f"Server listening on {listen_at}..")
    s.listen(server_config.backlog)

    while True:
        try:
            c, addr = s.accept()
            threading.Thread(target=handler, args=(c, addr, server_config.root)).start()
        except KeyboardInterrupt:
            print("\rStopping server..")
            s.close()
            return 127
    s.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
