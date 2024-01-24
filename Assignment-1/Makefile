start:
	docker-compose up -d lb
	sleep 2
	curl -X POST http://localhost:5000/add -d '{"n": 3, "hostnames": ["s1", "s2", "s3"]}' 

build:
	docker-compose build 

clean:
	make clean_servers
	-docker-compose down

clean_servers:
	-docker rm -f $$(docker ps -aqf "ancestor=serverimg")

remove_images:
	-docker rmi -f serverimg lb:1.1



	