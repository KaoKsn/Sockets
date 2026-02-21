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

#define MAXSIZE 512

void *get_addr_in(struct sockaddr *sa);

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "Usage: client host port\n");
        return 1;
    }
    // TODO: validate port number.
    int status, sockfd, bytes_received;
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
            perror("client: ");
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
    if (p == NULL) {    // Failed every connect attempt.
        fprintf(stderr, "client: every attempt to connect() failed!\n");
        close(sockfd);
        return 3;
    }

    printf("Connected to %s: %s on port %s\n", argv[1], ipstr, argv[2]);
    bytes_received = recv(sockfd, buffer, MAXSIZE - 1, 0);
    if (bytes_received == -1) {
        perror("client: recv() failed!\n");
        exit(4);
    }
    printf("client: received %s\n", buffer);
    close(sockfd);
    return 0;
}

void *get_addr_in(struct sockaddr *sa)
{
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
