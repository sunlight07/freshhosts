#!/usr/bin/env python
import os
import sys
import socket

def getip(address):
	dns = "2001:4860:4860::8888"
	return os.popen("dig @%s %s AAAA | grep AAAA | grep -oE :*[0-9a-fA-F]{4}:[0-9a-fA-F:]* | grep -v %s" % (dns, address, dns)).read().strip()

# fetch hosts from googlecode
print "connect..."
ip = getip("ipv6-hosts.googlecode.com")
sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

sock.connect((ip, 80))
sock.send('GET ipv6-hosts.googlecode.com/hg/hosts HTTP/1.1\r\nConnection: close\r\n\r\n')

print "fetch hosts..."
oldfile = file("old-hosts", "w")
while True:
	data = sock.recv(4096)
	if len(data) == 0: break
	oldfile.write(data)
oldfile.close()
sock.close()

print "clean host..."
flag = False
oldfile = file("old-hosts", "r")
cleanfile = file("old-hosts-clean", "w")
for line in oldfile:
	if not flag and line[0] == '#':
		flag = True
	if flag:
		line = line[0:line.find("#")].strip()
		if len(line) > 0:
			cleanfile.write(line + "\n")
cleanfile.close()
oldfile.close()

os.system("mv old-hosts-clean old-hosts")

print "nslookup..."
oldfile = file("old-hosts", "r")
os.system("echo \#`date` > new-hosts")
newfile = file("new-hosts", "a")
for line in oldfile:
	parts = line.strip().split(" ")
	if (len(parts) != 2): continue
	result = getip(parts[1])
	if len(result) == 0:
		result = parts[0]
	newfile.write(result + " " + parts[1] + "\n")
oldfile.close()
newfile.close()

os.system("echo \#`date` >> new-hosts")
print "done"
