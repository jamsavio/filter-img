import argparse
import sys
import socket
from PIL import Image

def main(argv):

    ClientMultiSocket = socket.socket()
    host = '127.0.0.1'
    port = 2004

    try:
        ClientMultiSocket.connect((host, port))
    except socket.error as e:
        print(str(e))

    parser = argparse.ArgumentParser()
    parser.add_argument("image_file", type=str)
    parser.add_argument("output_name", type=str)
    parser.add_argument("transformation", type=str)
    parser.add_argument("rows", nargs='?', default=2, type=int)
    parser.add_argument("columns", nargs='?', default=2, type=int)

    args = parser.parse_args()

    image_to_transform = Image.open(args.image_file)
    width, height = image_to_transform.size

    if image_to_transform.mode != 'RGB':
        print>> sys.stderr, "Unknown color mode: {0}"\
                                            .format(image_to_transform.mode)
        exit(4)

    bytes_img = image_to_transform.tobytes()
    ClientMultiSocket.send(bytes_img)
    ClientMultiSocket.send(str("$data$"+str(args.rows)+","+str(args.columns)+","+str(args.transformation)+","+str(width)+","+str(height)).encode())
    ClientMultiSocket.shutdown(socket.SHUT_WR)

    photo = b""
    chunk = ClientMultiSocket.recv(4096)
    while chunk:
        photo += chunk
        chunk = ClientMultiSocket.recv(4096)

    try:
        img = Image.frombytes(data=photo, size=(width, height), mode="RGB")
        img.show(title=args.output_name)   
        img.save(args.output_name)   
    except:
        print(photo.decode("utf-8"))

    ClientMultiSocket.close()

if __name__ == '__main__':
    main(sys.argv)