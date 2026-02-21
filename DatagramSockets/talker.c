/**
    *
    * talker.c -- unconnected datagram socket "client".
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
    if (argc != 4) {
        fprintf(stderr, "Usage: client host port message\n");
        return 1;
    }
    int port = atoi(argv[2]);
    if (port <= 0 || port > 65535) {
        fprintf(stderr, "Suggest a valid port number!\n");
        return 1;
    }
    if (argv[3]) {
        int status, sockfd, bytes_sent;
        struct addrinfo hints, *server, *p;

        memset(&hints, 0, sizeof(hints));
        hints.ai_family = AF_INET6;
        hints.ai_socktype = SOCK_DGRAM;
        status = getaddrinfo(argv[1], argv[2], &hints, &server);

        if (status != 0) {
            fprintf(stderr, "gai_error: %s\n", gai_strerror(status));
            return 2;
        }
        for (p = server; p != NULL; p = p->ai_next) {
            sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
            if (sockfd == -1) {
                perror("talker (socket): ");
                continue;
            }
            break;
        }
        if (p == NULL) {
            fprintf(stderr, "talker: failed to received a socket file descriptor!\n");

        }
        bytes_sent = sendto(sockfd, argv[3], strlen(argv[3]), 0, p->ai_addr, p->ai_addrlen);
        if (bytes_sent != -1)
            printf("talker: sent %d bytes to %s\n", bytes_sent, argv[1]);
        close(sockfd);
        freeaddrinfo(server);
    }
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
