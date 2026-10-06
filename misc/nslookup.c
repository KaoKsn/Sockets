// Perform domain ip address lookups for a given domain //
#include <arpa/inet.h>
#include <netdb.h> // addrinfo
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>

int main(void) {
    char *domain = NULL;
    domain = calloc(32, sizeof(char));
    if (!domain) {
        return 1;
    }
    printf("domain: ");
    fgets(domain, 32, stdin);
    domain[strlen(domain) - 1] = '\0';

    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    int status = getaddrinfo(domain, NULL, &hints, &res);

    if (status != 0) {
        fprintf(stderr, "failed: %s\n", gai_strerror(status));
        free(domain);
        return 1;
    }

    char ip[INET6_ADDRSTRLEN];
    for (struct addrinfo *p = res; p != NULL; p = p->ai_next) {
        memset(ip, 0, INET6_ADDRSTRLEN);
        if (p->ai_family == AF_INET) {
            struct sockaddr_in *ipv4 = (struct sockaddr_in *)p->ai_addr;

            inet_ntop(p->ai_family, &(ipv4->sin_addr), ip, INET6_ADDRSTRLEN);
        } else {
            struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)p->ai_addr;
            inet_ntop(p->ai_family, &(ipv6->sin6_addr), ip, INET6_ADDRSTRLEN);
        }
        printf("\t%s\n", ip);
    }
    freeaddrinfo(res);
    free(domain);
    return 0;
}
