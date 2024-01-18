start:
	docker-compose up -d lb 

build:
	docker-compose build 

clean:
	-docker rm -f $$(docker ps -aqf "ancestor=serverimg")
	-docker-compose down


	