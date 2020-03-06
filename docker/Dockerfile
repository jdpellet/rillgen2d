FROM centos:8

RUN yum update -y && yum install gcc -y

COPY rillgen2d.c /usr/src/rillgen2d/rillgen2d.c

WORKDIR /usr/src/rillgen2d

RUN gcc rillgen2d.c -o rillgen2d -lm

ENV PATH=/usr/src/rillgen2d:$PATH

CMD ["/usr/src/rillgen2d/rillgen2d"]
