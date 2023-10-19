# Uncomment this to pass the first stage
import socket


class Request:
    def __init__(self) -> None:
        self.method = "GET"
        self.url = "/"
        self.body = ""


def parseReq(data):
    data = data.decode()
    req = Request()
    start_line = data.split("\r\n")[0].split(" ")
    req.method = start_line[0]
    req.url = start_line[1]
    return req


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    with server_socket:
        conn, _ = server_socket.accept()  # wait for client
        with conn:
            data = conn.recv(1024)
            req = parseReq(data)
            if req.url == "/":
                conn.send("HTTP/1.1 200 OK\r\n\r\n".encode())
            else:
                conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())


if __name__ == "__main__":
    main()
