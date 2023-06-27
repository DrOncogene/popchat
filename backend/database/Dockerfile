FROM mongo:latest

COPY ./popchat-db.dump /tmp/db.dump 

EXPOSE 27017

CMD mongod --fork --logpath /var/log/mongodb.log; \
    mongorestore --uri 'mongodb://localhost:27017' --nsInclude=popchat.\* --archive < /tmp/db.dump; \
    mongod --shutdown; \
    docker-entrypoint.sh mongod