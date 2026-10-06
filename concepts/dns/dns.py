import socket, sys

DEFAULT_PORT = 80


def main():
    if len(sys.argv) < 2:
        print("Usage: python dns.py domain [port]")
        sys.exit(1)
    domain, port = sys.argv[1], DEFAULT_PORT
    if len(sys.argv) >= 3:
        port = sys.argv[2]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    info = socket.getaddrinfo(domain, port)

    st = set()
    # record is 5 tuple. (family, socktype, proto, canoname, _)
    for record in info:
        st.add(record[4][0])
    for ip in st:
        print(ip)


if __name__ == "__main__":
    main()
