# PopChat - The Chat App

Popchat is a real time web-based chat application built with websockets (ws)
- users are available generally, any user can search any other user by their username
- users can chat one on one and also in rooms
- any user can create and add any other user to a room, however, users can block being added to rooms
- there is message persistence on the backend (this will change later)
- more features  

## Technologies
- Frontend:
    - Svelte
    - SocketIO client
    - TypeScript  
    - TailwindCSS  
&nbsp;  
- Backend:
    - Python3 (version 3.11)
    - FASTAPI
    - Python-socketio
    - JWT authentication (fastapi_jwt_auth)
    - Database: MongoDB
    - Cache: Redis
    - Docker
    - NGINX
    - RabbitMQ


## Running the app
Ensure python3.11 is installed  
To run the app, open the root directory of the project  
1. Get mongodb database running locally or with docker on the default port. For docker:  
- install docker: [docker docs](https://docs.docker.com/engine/install/)
- run the mongodb container: ```docker run -p 27017:27017 --name mongodb mongo:latest```
&nbsp;  
2. Run the client server:  
- ```cd client```  
- ```npm install```  
- ```npm run dev```  
&nbsp;  
3. In another terminal window, run the backend server:  
- ```cd backend```  
- Create .env file in the backend directory and add the following environment variables (DB_* env variables can be omitted if mongodb is running on the default settings and does not need authentication):
    - ```AUTHJWT_SECRET_KEY={ value }``` (set **value** to a secret key of your choosing)  
    - ```DB_NAME={ database name }```  
    - ```DB_PORT={ db port }```  
    - ```DB_HOST={ db host }```  
    - ```DB_USER={ db user }```  
    - ```DB_PASSWD={ db password }```  
- ```pipenv install```  
- ```python3 wsgi.py```  
**NOTE**: you can also set *DB_NAME*, *DB_HOST* and *DB_PORT* only if mongod is running on different port and host without authentication enabled, otherwise all DB_* env variables must be given.  
&nbsp;
&nbsp;  
ENJOY!