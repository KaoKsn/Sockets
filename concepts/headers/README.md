tcp header validation using:

checksum, data, tcp header, source/dest ip => change in any return failed.

tcp_addrs_\d.txt => use to create the pseudo IP header.
	format:
		source dest

tcp_data_\d.dat -> creates the tcp header, extract the checksum and use the others to validate
