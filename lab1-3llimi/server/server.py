import argparse
import socket
import os
import sys

BUFFER_SIZE = 20480


def sanitize_filename(filename):
    return os.path.basename(filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="Port number to listen on")
    args = parser.parse_args()

    server_address = ("0.0.0.0", args.port)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(server_address)
        print(f"Server listening on {server_address}...")

        expected_seqno = 0
        file = None
        file_name = ""
        file_size = 0
        received_bytes = 0

        try:
            while True:
                try:
                    data, client_address = s.recvfrom(BUFFER_SIZE)
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    continue

                if not data:
                    continue

                message = data.decode(errors='ignore')
                message_type = message[0]

                if message_type == 's':  # Start of file transfer
                    try:
                        _, seqno, file_name, file_size = message.split('|')
                        file_size = int(file_size)
                        file_name = sanitize_filename(file_name)
                        expected_seqno = (int(seqno) + 1) % 2
                    except ValueError:
                        print("Invalid start packet format. It will be Ignored...")
                        continue

                    file_path = os.path.join(script_dir, file_name)

                    if os.path.exists(file_path):
                        print(
                            f"Warning: Overwriting existing file: {file_path}")

                    file = None
                    received_bytes = 0
                    print(f"Receiving file: {file_path} ({file_size} bytes)")

                elif message_type == 'd':
                    header_end = data.find(b'|', 2)
                    if header_end == -1:
                        print(
                            "Invalid data format received. This packet will be skipped...")
                        continue

                    try:
                        seqno = int(data[2:header_end].decode())
                    except ValueError:
                        print(
                            "Invalid sequence number received. This packet will be skipped...")
                        continue

                    file_data = data[header_end + 1:]

                    if seqno == expected_seqno:
                        if file is None:
                            file = open(file_path, "wb")
                        file.write(file_data)
                        received_bytes += len(file_data)
                        expected_seqno = (seqno + 1) % 2

                    if received_bytes >= file_size:
                        print(f"File {file_path} received successfully.")
                        if file:
                            file.close()
                        file = None

                ack_packet = f"a|{expected_seqno}".encode()
                s.sendto(ack_packet, client_address)

        except KeyboardInterrupt:
            print("Server shutting down...")
            if file:
                file.close()
            sys.exit(0)


if __name__ == "__main__":
    main()
