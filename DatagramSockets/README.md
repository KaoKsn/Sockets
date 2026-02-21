# Client-Server Model with UNIX Unconnected Datagram Sockets.

## Structure and Files
    .
    ├── listener.c
    ├── makefile
    ├── README.md
    └── talker.c

1 directory, 4 files

---- 

## Compile and Test:
```bash
    make
    ./listener port
    ./talker host port message
```


Ensure that both the port numbers are the same, so that the *talker* can talk to the *listener*.

---- 

## Libraries and tools required:
    gcc, GNU make, libc
