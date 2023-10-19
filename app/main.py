# Uncomment this to pass the first stage
import socket


class Request:
    def __init__(self):
        self.method = "GET"
        self.url = "/"
        self.header = dict({})
        self.body = ""

    def __str__(self):
        return f"Method={self.method}\n url={self.url}\n header={self.header}\nbody={self.body}"


class Response:
    def __init__(self, status=""):
        self.status = status
        self.header = dict({})
        self.body = ""


def parse_req(data):
    req = Request()
    arr = data.decode().split("\r\n")
    # setup start_line
    start_line = arr[0].split(" ")
    req.method = start_line[0]
    req.url = start_line[1]
    # setup headers
    for i in range(1, len(arr) - 2):
        key, value = arr[i].split(": ", 1)
        req.header[key] = value
    # body
    req.body = arr[-1]
    return req


def encode_res(data: Response) -> bytes:
    status_line = f"HTTP/1.1 {data.status}"
    # setup header
    if data.body:
        data.header["Content-Length"] = len(data.body)
    header = (
        "\r\n" + ("\r\n".join([f"{key}:{value}" for key, value in data.header.items()]))
        if data.header
        else ""
    )
    #
    return (status_line + header + "\r\n\r\n" + data.body).encode()


method_map = {"GET": {"abs": {}, "rel": {}}, "POST": {"abs": {}, "rel": {}}}


def setup_route(route, fn, method):
    if route[-1] == "/":
        method_map[method]["rel"]["*" + route[:-1]] = fn
    else:
        method_map[method]["abs"]["*" + route] = fn


def get(route):
    def deco(func):
        setup_route(route, func, "GET")

    return deco


def post(route):
    def deco(func):
        setup_route(route, func, "POST")

    return deco


def handle_request(conn, req):
    res = Response("404 Not Found")
    m = method_map[req.method]
    url = "*" + req.url.rstrip("/")
    fn = m["abs"].get(url, m["rel"].get(url, None))
    if fn == None:
        path = url
        for i in range(len(url) - 1, 0, -1):
            if url[i] == "/":
                path = path[:i]
                fn = m["rel"].get(path)
                if fn != None:
                    break
                continue
        if fn != None:
            fn(req, res)
    else:
        fn(req, res)
    conn.send(encode_res(res))


# setting up routes
@get("/")
def fn(req, res):
    if req.url == "/":
        res.status = "200 Ok"
    else:
        res.status = "404 Not Found"


@get("/echo/")
def fn(req, res):
    arr = req.url.split("/", 2)
    if len(arr) > 2:
        res.status = "200 OK"
        res.body = arr[2]
        res.header["Content-Type"] = "text/plain"
    else:
        res.status = "404 Not Found"


@get("/user-agent")
def fn(req, res):
    res.status = "200 OK"
    res.body = req.header["User-Agent"]
    res.header["Content-Type"] = "text/plain"


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
            req = parse_req(data)
            handle_request(conn, req)


if __name__ == "__main__":
    main()
