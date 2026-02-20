/**
 *
 *
 * server.c -- a stream socket server.
 *
 *
**/

// TODO: remove any trailing whitespaces.
#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define PORT "1024"
#define BACKLOG 10

void sigchild_handler(int s);
void *get_addr_in(struct sockaddr *sa);
int getport(struct sockaddr *sa);

int main(void)
{
	// server.
	int sockfd, status, new_fd;
	struct addrinfo hints, *server, *p;

	// client.
	struct sockaddr_storage client;
	socklen_t addrlen = sizeof(struct sockaddr_storage);
    char ipstr[INET_ADDRSTRLEN];

	memset(&hints, 0, sizeof(hints));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_flags = AI_PASSIVE;

	status = getaddrinfo(NULL, PORT, &hints, &server);
	if (status != 0) {
		fprintf(stderr, "gai_error: %s\n", gai_strerror(status));
		return 1;
	}
	// Loop over and bind() to port 1024 on localhost.
	for (p = server; p != NULL; p = p->ai_next) {
		sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
		if (sockfd == -1) {
			perror("server: socket() error\n");
			continue;
		}
		// Address "Address already in use error!"
		int yes = 1;
		if (setsockopt(sockfd, SOL_SOCKET , SO_REUSEADDR, &yes, sizeof(yes)) == -1) {
			perror("server: Couldn't free address for use!\n");
			close(sockfd);
			freeaddrinfo(server);
			exit(1);
		}

		if (bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
			perror("server: bind() error!\n");
			continue;
		}
		// If everything works well, use the socket.
		break;
	}
	freeaddrinfo(server);

	if (p == NULL) {
		fprintf(stderr, "server failed to bind()!\n");
		exit(1);
	}

	// listen
	if (listen(sockfd, BACKLOG) == -1) {
		perror("server: listen()\n");
		exit(1);
	}

	struct sigaction sa;
	sa.sa_handler = sigchild_handler; // reap all dead processes.
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    if (sigaction(SIGCHLD, &sa, NULL) == -1) {
        perror("sigaction\n");
        exit(1);
    }

	printf("server @ localhost %s: waiting for incoming connection requests....\n", PORT);

	while (1) {	// main accept() loop
		new_fd = accept(sockfd, (struct sockaddr *)&client, &addrlen);
		if (new_fd == -1) {
			fprintf(stderr, "server: accept() failed!\n");
			continue;
		}

        // print the ip address and port of the client.
        inet_ntop(client.ss_family, get_addr_in((struct sockaddr *)&client), ipstr, sizeof(ipstr));
        printf("Server: connection accepted from: %s, port: %d\n", ipstr, getport((struct sockaddr *)&client));

		// fork a child process to handle the connection.
        int child = fork();
        if (child == -1) {
            perror("fork() failed!\n");
        } else if (child == 0) { // child
            close(sockfd); // child doesn't need the listening sockfd.
            char *msg = "Hello, client\n";
            if (send(new_fd, msg, strlen(msg), 0) == -1)
                perror("send()\n");
            close(new_fd);
            exit(0);
        }
        close(new_fd);  // parent doesn't need this.
	}
	return 0;
}

void sigchild_handler(int s)
{
    (void) s; // suppress unused variable warning.

    // waitpid() might override errno, so we save and restore it.
    int saved_errno = errno;
    while (waitpid(-1, NULL, WNOHANG) > 0);
    errno = saved_errno;
}

// get sockaddr, IPv4, IPv6.
void *get_addr_in(struct sockaddr *sa)
{
    if (sa == NULL) 
        return NULL;

    if (sa->sa_family == AF_INET) { // IPv4
        struct sockaddr_in *ipv4 = (struct sockaddr_in *)sa;
        return &(ipv4->sin_addr);
    }
    struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)sa;
    return &(ipv6->sin6_addr);
}

// get port number
int getport(struct sockaddr *sa)
{
    int port = -1;
    if (sa) {
        if (sa->sa_family == AF_INET)
            return htons(((struct sockaddr_in *)sa)->sin_port);
        else
            return htons(((struct sockaddr_in6 *)sa)->sin6_port);
    }
    return port;
}
