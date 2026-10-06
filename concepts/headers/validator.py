import sys

"""
    Build the pseudo IP header

    Extract the checksum from the existing TCP segment

    Build the version of the TCP segment with the checksum replaced with 0x0

"""


def ip_to_bytestring(ip: str) -> bytes:
    octets = ip.split(".")
    if len(octets) != 4:
        print("Invalid IP read. Quitting", file=sys.stderr)
        sys.exit(1)

    res = b""
    for octet in octets:
        octet = int(octet)
        if 0 <= octet <= 255:
            res += int(octet).to_bytes(1, "big")
        else:
            print("Invalid IP read. Quitting", file=sys.stderr)
            sys.exit(1)

    return res


def construct_pseudo_ip_header(ip_file, header_file) -> bytes:
    """
    Constructing the pseudo IP header

    +-------------- 32 bits ------------+
    +--------+--------+--------+--------+
    |           Source Address          |
    +--------+--------+--------+--------+
    |         Destination Address       |
    +--------+--------+--------+--------+
    |  Zero  |  PTCL  |    TCP Length   |
    +--------+--------+--------+--------+

    Delimiter(+) on a byte, PTCL: 0x06 for TCP.
    """
    pseudo_ip_header, magic = b"", b"\x00\x06"
    with open(ip_file, "r") as file:
        line = file.read().strip().split()
        for ip in line:
            pseudo_ip_header += ip_to_bytestring(ip)

    pseudo_ip_header += magic

    with open(header_file, "rb") as file:
        info = file.read()
        tcp_length = len(info)
        pseudo_ip_header += tcp_length.to_bytes(2, "big")

    return pseudo_ip_header


def extract_tcp_segment(header_file: str) -> tuple[int, bytes]:
    """
        TCP segment: 0                   1                   2                   3
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |          Source Port          |       Destination Port        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                        Sequence Number                        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Acknowledgment Number                      |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |  Data |           |U|A|P|R|S|F|                               |
    | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
    |       |           |G|K|H|T|N|N|                               |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |           Checksum            |         Urgent Pointer        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Options                    |    Padding    |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                             data                              |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """
    with open(header_file, "rb") as file:
        tcp_segment = file.read()
        checksum = int.from_bytes(tcp_segment[16:18], "big")

    # Replace the checksum in the tcp segment with 0x0.
    tcp_zero_cksum = tcp_segment[:16] + b"\x00\x00" + tcp_segment[18:]

    return checksum, tcp_zero_cksum


def tcp_checksum_calc(data: bytes) -> int:
    offset, total = 0, 0
    while offset < len(data):
        # Slicing 2 bytes.
        word = int.from_bytes(data[offset : offset + 2], "big")

        total += word
        total = (total & 0xFFFF) + (total >> 16)  # carry around
        offset += 2

    return (~total) & 0xFFFF  # one's complement


def main():
    if len(sys.argv) < 3:
        print("Usage: python validator.py ip.txt header.dat")
        sys.exit(1)
    ip_file, header_file = sys.argv[1], sys.argv[2]

    # Construct the Pseudo IP header
    print("[+] Constructing the pseudo IP header")
    pseudo_ip_header = construct_pseudo_ip_header(ip_file, header_file)

    # Extract the TCP header and data
    checksum, tcp_zero_cksum = extract_tcp_segment(header_file)
    print("[+] Checksum Extraction Complete")

    """
        Validate the checksum

        16 bits 1's complement of the 1's complement sum of all 16 bit words in the tcp segment.
    """

    # Force an even length
    if len(tcp_zero_cksum) % 2 == 1:
        tcp_zero_cksum += b"\x00"
    data = pseudo_ip_header + tcp_zero_cksum

    calc_checksum = tcp_checksum_calc(data)

    if calc_checksum == checksum:  # short (%hu)
        print("\033[32m[+] PASS\033[0m")
    else:
        print("\033[31m[-] FAIL\033[0m")


if __name__ == "__main__":
    main()
