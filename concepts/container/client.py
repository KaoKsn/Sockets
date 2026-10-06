"""
Use the unix socket provided by docker to check for images.
docker:
   python client.py | jq '.[].RepoTags.[0]//null'

Docker API documentation: https://docs.docker.com/reference/api/engine/version/v1.56/

Podman API documentation: https://github.com/podman-container-tools/podman/tree/main/pkg/bindings

"""

import socket, sys, json

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

sock_paths = {
    "podman": ["/run/podman/podman.sock", "/run/user/1000/podman/podman.sock"],
    "docker": ["/run/docker.sock"],
}

HEADER_END = "\r\n\r\n"
try:
    provider = "docker"
    if provider not in sock_paths:
        sys.exit(1)
    for path in sock_paths[provider]:
        try:
            s.connect(path)
        except PermissionError as e:
            print(f"Failed to connect to {path}: {e}", file=sys.stderr)
        else:
            break
    request = (
        "GET /images/nginx:1.31-alpine/json HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Connection: close\r\n"
        "\r\n"
        "GET /v6.1.1/libpod/images/json HTTP/1.1\r\n"
    )

    # /v1.56 {"message":"client version 1.56 is too new. Maximum supported API version is 1.55"}
    s.sendall(request.encode())

    response = b""
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data

    response = response.decode()
    header, body = response.split(HEADER_END, 1)

    body = json.loads(body)
    print(json.dumps(body, indent=2))
    body = response.split("\r\n\r\n")[1].split("\n")[1]  # 4ae9
    if body:
        body = json.loads(body)
        for container in body:
            repotags = container["RepoTags"]
            for repotag in repotags:
                if repotag:
                    print(repotag)

except Exception as e:
    print(e, file=sys.stderr)
finally:
    s.close()
