FROM gcc:4.9

COPY rillgen2d.c /usr/src/rillgen2d/rillgen2d.c
 
RUN cd /usr/src/rillgen2d && \
    gcc rillgen2d.c -o rillgen2d -lm -g 

ENV PATH=/usr/src/rillgen2d/:$PATH

WORKDIR /data

CMD ["rillgen2d"]
