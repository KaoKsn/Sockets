CC = gcc
CFLAGS = -Wall -Wextra -pedantic

all: server client
	@make clean &>/dev/null
	@echo "Complete with no errors."

server: server.c
	@$(CC) $(CFLAGS) server.c -o server

client: client.c
	@$(CC) $(CFLAGS) client.c -o client

clean:
	@rm -f *.o *.s *.asm

