Build with

docker build -t flaskdock .

Run with (or something like if the volume location is different)

docker run -p 5000:80 --volume=/Users/dspeed2/Documents/FlaskDocker/myapp:/app flaskdock

Tail logs with

docker logs -f cool_beaver

Get the name of the container with (the names column)

docker ps

Stop the daemon version with

docker stop cool_beaver

Stop the non deamon with ctrl-c


