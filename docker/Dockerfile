FROM gcc:4.9

COPY rillgen2d.c /usr/src/rillgen2d/rillgen2d.c

WORKDIR /usr/src/rillgen2d
 
RUN gcc rillgen2d.c -o rillgen2d -lm

CMD ["./rillgen2d"]
