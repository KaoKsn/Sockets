badrequest = (
    "HTTP/1.1 400 Bad Request\r\n"
    "Connection: close\r\n"
    "\r\n"
)

forbidden = (
    "HTTP/1.1 403 Forbidden\r\n"
    "Connection: close\r\n"
    "\r\n"
)

notfound = (
    "HTTP/1.1 404 Not Found\r\n"
    "Content-Type: text/html\r\n"
    "Content-Length: 48\r\n"
    "Connection: close\r\n"
    "\r\n"
    '<h1 style="top=50%; left=50%">404 Not Found</h1>'
)
