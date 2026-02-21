CC = gcc
CFLAGS = -Wall -Wextra -pedantic

all: listener talker
	@make clean &>/dev/null
	@echo "Complete with no errors."

listener: listener.c
	@$(CC) $(CFLAGS) listener.c -o listener

talker: talker.c
	@$(CC) $(CFLAGS) talker.c -o talker

clean:
	@rm -f *.o *.s *.asm

