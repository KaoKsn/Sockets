CC = gcc
CFLAGS = -Wall -Wextra -pedantic -g

BUILD_DIR = ./build

$(BUILD_DIR)/$(target): server client
	@echo "Build Complete"

all: server client
	@make clean &>/dev/null
	@echo "Complete with no errors."

server: server.c
	@mkdir -p ./build/
	@$(CC) $(CFLAGS) server.c -o $(BUILD_DIR)/server

client: client.c
	@$(CC) $(CFLAGS) client.c -o $(BUILD_DIR)/client

clean:
	rm -rf $(BUILD_DIR)

