# Some common English words
import sys
import socket
import random

from words import WORDS

# How many bytes is the word length?
WORD_LEN_SIZE = 2


def usage():
    print("usage: wordserver.py port", file=sys.stderr)


def build_word_packet(word_count):
    word_packet = b""
    word_list = []

    for _ in range(word_count):
        word = random.choice(WORDS)
        word_bytes = word.encode()
        word_len = len(word_bytes)
        word_len_bytes = word_len.to_bytes(WORD_LEN_SIZE, "big")

        word_packet += word_len_bytes + word_bytes
        word_list.append(word)

    return word_packet, word_list


def send_words(s):
    word_count = random.randrange(1, 10)

    word_packet, word_list = build_word_packet(word_count)

    s.sendall(word_packet)

    return word_list


def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", port))
    s.listen()

    while True:
        print("-----------------------")
        print("Waiting for connections")
        print("-----------------------")

        new_s, connection_info = s.accept()

        print(f"Got connection from {connection_info}")

        word_list = send_words(new_s)

        print(f"Sent words: {','.join(word_list)}")

        new_s.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
