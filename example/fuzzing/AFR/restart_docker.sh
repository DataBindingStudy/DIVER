docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

docker run -p 8080:8080 tomcat_spring_jdk11

