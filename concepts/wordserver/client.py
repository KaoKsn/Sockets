"""
packets: abstractions over raw bytes of data that recv() gives us.

Reading and inspecting stream of bytes as packets.

Code must work on an positive value of recv from 1, 4096
Code must work on words of len from (1, 65535)

"""

import sys
import socket
import random

# How many bytes is the word length
# Eg: [2, hi]
WORD_LEN_SIZE = 2


def usage():
    print("usage: wordclient.py server port", file=sys.stderr)


packet_buffer = b""


def get_next_word_packet(s):
    """
    Return the next word packet from the stream.

    The word packet consists of the encoded word length followed by the
    UTF-8-encoded word.

    Returns None if there are no more words, i.e. the server has hung
    up.
    """
    global packet_buffer

    while True:
        # If we have enough bytes to read the word length prefix,
        while len(packet_buffer) >= WORD_LEN_SIZE:
            target_size = int.from_bytes(packet_buffer[:WORD_LEN_SIZE], "big")
            total_packet_size = target_size + WORD_LEN_SIZE

            if total_packet_size > len(packet_buffer):
                break  # read more bytes from the socket.
            else:  # Just read a complete packet, remove the packet from the buffer and return it.
                word_packet = packet_buffer[:total_packet_size]
                # Remove the word from the global buffer.
                packet_buffer = packet_buffer[total_packet_size:]
                return word_packet
        """
        Not to be moved to the beginning because, the server might just send b'':
        example: you get all the content in oneshot, you read a single packet and return it to main.
               but when it asks you to read the next packet, the server will send b'' which closes the connection
        """
        buf_size = [1, 5, 25, 128, 1024, 4096]
        chunk = s.recv(random.choice(buf_size))
        if not chunk:
            return None
        packet_buffer += chunk


def extract_word(word_packet):
    """Extract a word from a word packet.

    word_packet: a word packet consisting of the encoded word length
    followed by the UTF-8 word.

    Returns the word decoded as a string.
    """
    target_size = int.from_bytes(word_packet[:WORD_LEN_SIZE], "big")
    total_packet_size = target_size + WORD_LEN_SIZE
    word = word_packet[WORD_LEN_SIZE:total_packet_size].decode(
        "utf-8"
    )  # 2: 2 + target_size
    return word


# Do not modify:
def main(argv):
    try:
        host = argv[1]
        port = int(argv[2])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    print("Getting words:")

    while True:
        word_packet = get_next_word_packet(s)

        if word_packet is None:
            break

        word = extract_word(word_packet)

        print(f"    {word}")

    print("Closing socket")
    s.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
