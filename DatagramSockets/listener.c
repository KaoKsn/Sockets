/**
 *
 *
 * listener.c - listen for incoming packets at the specified port.
 *
 *
**/

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
void print_packet_info(char *ipstr, int bytes_recv, char *buffer);

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Usage: listener port\n");
        return 1;
    }
    int status, sockfd;
    struct addrinfo hints, *servinfo, *p;
    char ipstr[INET6_ADDRSTRLEN];
    
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET6;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_flags = AI_PASSIVE;

    status = getaddrinfo(NULL, argv[1], &hints, &servinfo);
    if (status != 0) {
        fprintf(stderr, "gai_error: %s\n", gai_strerror(status));
        return 2;
    }

    for (p = servinfo; p != NULL; p = p->ai_next) {
        sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (sockfd == -1) {
            perror("listener: socket");
            continue;
        }
        if (bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            perror("listener: bind");
            close(sockfd);
            continue;
        }
        break;
    }
    freeaddrinfo(servinfo);

    if (p == NULL) {
        fprintf(stderr, "Complete failure to bind the sockets!\n");
        exit(3);
    }

    printf("listener: waiting to recvfrom... \n");
    
    char buffer[MAXSIZE] = {'\0'};
    struct sockaddr_storage their_addr;
    socklen_t addrlen = sizeof(struct sockaddr_storage);
    int bytes_recv = recvfrom(sockfd, buffer, sizeof(buffer) - 1, 0, (struct sockaddr *)&their_addr, &addrlen);
    if (bytes_recv == -1) {
        perror("listener: recvfrom");
        close(sockfd);
        exit(4);
    }

    inet_ntop(their_addr.ss_family, (struct sockaddr *)&their_addr, ipstr, INET6_ADDRSTRLEN);
    print_packet_info(ipstr, bytes_recv, buffer);
    close(sockfd);
	return 0;
}

// print recvfrom information.
void print_packet_info(char *ipstr, int bytes_recv, char *buffer) {
    printf("Packet: \n");
    printf("\taddress: %s\n", ipstr);
    printf("\tbytes: %d\n", bytes_recv);
    printf("\tContent: %s\n", buffer);
}

// get sockaddr, IPv4, IPv6.
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
