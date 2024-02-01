#makefile
CC = g++
CFLAGS = -g -W -Wall -Wno-unused-parameter -Wno-unused-variable -std=c++17 -pedantic
.PHONY : clean
all : server
server: ./build/server.o 
	$(CC) build/server.o -o bin/server
	
build/server.o: src/server.cpp
	$(CC) $(CFLAGS) -c src/server.cpp -o build/server.o

clean:
	rm -f build/*.o bin/server 
	
init:
	mkdir build/
	mkdir bin/
