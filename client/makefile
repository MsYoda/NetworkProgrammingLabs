#makefile
CC = g++
CFLAGS = -g -W -Wall -Wno-unused-parameter -Wno-unused-variable -std=c++17 -pedantic
.PHONY : clean
all : client
client: ./build/client.o 
	$(CC) build/client.o -o bin/client
	
build/client.o: src/client.cpp
	$(CC) $(CFLAGS) -c src/client.cpp -o build/client.o

clean:
	rm -f build/*.o bin/client 
