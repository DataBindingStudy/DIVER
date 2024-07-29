FROM ubuntu

USER root
RUN apt update
RUN apt install openjdk-11-jdk -y

RUN useradd -m -s /bin/bash tomcatuser
USER tomcatuser
WORKDIR /home/tomcatuser
COPY apache-tomcat-9.0.60.tar.gz /home/tomcatuser
RUN tar -zxvf apache-tomcat-9.0.60.tar.gz
COPY helloworld.war apache-tomcat-9.0.60/webapps

EXPOSE 8080
CMD ["/home/tomcatuser/apache-tomcat-9.0.60/bin/catalina.sh", "run"]
