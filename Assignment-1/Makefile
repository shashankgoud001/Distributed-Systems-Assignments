start:
	docker-compose up  lb 

build:
	docker-compose build 

clean:
	-docker rm -f $$(docker ps -aqf "ancestor=serverimg")
	-docker-compose down


	