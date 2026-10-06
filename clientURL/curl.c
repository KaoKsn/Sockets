/**
 *
 * client.c -- a stream socket client.
 *
 *
 */

#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#define MAXSIZE 1024 * 1024

void *get_addr_in(struct sockaddr *sa);

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: client host port\n");
        return 1;
    }
    int port = atoi(argv[2]);
    if (port <= 0 || port > 65535) {
        fprintf(stderr, "Suggest a valid port number!\n");
        return 1;
    }
    int status, sockfd = -1, bytes_received;
    struct addrinfo hints, *server, *p;
    char ipstr[INET6_ADDRSTRLEN] = {'\0'}, buffer[MAXSIZE] = {'\0'};

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    status = getaddrinfo(argv[1], argv[2], &hints, &server);
    if (status != 0) {
        fprintf(stderr, "gai_error: %s\n", gai_strerror(status));
        return 2;
    }
    for (p = server; p != NULL; p = p->ai_next) {
        sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (sockfd == -1) {
            perror("client");
            continue;
        }
        inet_ntop(p->ai_family, get_addr_in(p->ai_addr), ipstr, sizeof(ipstr));

        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            fprintf(stderr, "client: %s: ", ipstr);
            perror(NULL);
            close(sockfd);
            continue;
        }
        break;
    }
    freeaddrinfo(server);
    if (p == NULL) { // Failed every connect attempt.
        fprintf(stderr, "client: every attempt to connect() failed!\n");
        close(sockfd);
        return 3;
    }

    printf("Connected to %s: %s on port %s\n", argv[1], ipstr, argv[2]);

    printf("\x1b[32mSending a HTTP GET request\x1b[0m\n");
    // Send HTTP GET request
    char req[MAXSIZE] = {'\0'};
    int n = snprintf(req, sizeof(req),
                     "GET / HTTP/1.1\r\n"
                     "Host: %s\r\n"
                     "Connection: close\r\n"
                     "\r\n",
                     argv[1]);
    if (n < 0 || (size_t)n > MAXSIZE) {
        fprintf(stderr, "Request too long!\n");
        close(sockfd);
        return 4;
    }
    ssize_t sent = send(sockfd, req, strlen(req), 0);
    if (sent == -1) {
        perror("send");
        close(sockfd);
        return 4;
    }

    // Receive HTTP response (loop to handle larger responses)
    bytes_received = 0;
    memset(buffer, 0, sizeof(buffer));

    while ((bytes_received = recv(sockfd, buffer, MAXSIZE - 1, 0)) > 0) {
        buffer[bytes_received] = '\0';
        printf("client: received %s\n", buffer);
        // If you want to print the whole response without truncation,
        // use a dynamically growing buffer instead of MAXSIZE.
        memset(buffer, 0, sizeof(buffer));
    }

    if (bytes_received == -1) {
        perror("recv");
        close(sockfd);
        return 5;
    }
    close(sockfd);
    return 0;
}

void *get_addr_in(struct sockaddr *sa) {
    if (sa) {
        if (sa->sa_family == AF_INET) {
            struct sockaddr_in *ipv4 = (struct sockaddr_in *)sa;
            return &(ipv4->sin_addr);
        }
        struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)sa;
        return &(ipv6->sin6_addr);
    }
    return NULL;
}
