start:
	docker-compose up  lb 

build:
	docker-compose build 

clean:
	make clean_servers
	-docker-compose down

clean_servers:
	-docker rm -f $$(docker ps -aqf "ancestor=serverimg")


	