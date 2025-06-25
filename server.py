import socket, os, mimetypes
from datetime import datetime

HOST = 'localhost'
PORT = 8080
WWW_ROOT = 'www'

def log_request(method, path, code):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{now}] {method} {path} -> {code}')

def handle(conn):
    try:
        request = conn.recv(1024).decode()
        if not request:
            return
        try:
            method, path, _ = request.split('\r\n')[0].split()
        except ValueError as e:
            error_message = str(e)
            print(e)
        if method != 'GET':
            response = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n'
            conn.sendall(response.encode())
            log_request(method, path, 405)
            return
        if path == '/':
            path = '/index.html'
        file_path = os.path.join(WWW_ROOT, path.lstrip('/'))
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                body = f.read()
            ctype = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            headers = (f'HTTP/1.1 200 OK\r\nContent-Type: {ctype}\r\n'
                       f'Content-Length: {len(body)}\r\n\r\n').encode()
            conn.sendall(headers + body)
            log_request(method, path, 200)
        else:
            body = b'<h1>404 Not Found</h1>'
            headers = (f'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n'
                       f'Content-Length: {len(body)}\r\n\r\n').encode()
            conn.sendall(headers + body)
            log_request(method, path, 404)
    finally:
        conn.close()

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f'Serving on http://{HOST}:{PORT}')
        while True:
            conn, _ = s.accept()
            handle(conn)
