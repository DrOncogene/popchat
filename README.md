# PopChat - The Chat App

Popchat is a real time web-based chat application built with websockets (ws)

- users are available generally, any user can search any other user by their username
- users can chat one on one and also in rooms
- any user can create and add any other user to a room, however, users can block being added to rooms
- there is message persistence on the backend (this will change later)
- more features to come

## Technologies

- Frontend: - Svelte - SocketIO client - TypeScript
  - TailwindCSS  
    &nbsp;
- Backend:
  - Python3.11
  - FastAPI
  - Python-socketio
  - JWT authentication (fastapi_jwt_auth)
  - Database: MongoDB
  - ODM: BeanieODM
  - Cache: Redis
  - Docker
  - Web Server: NginX
  - Application Server: Uvicorn
  - Queue: RabbitMQ

## Running the app

Ensure python3.11 is installed  
To run the app, open the root directory of the project

1. Without docker compose. Get MongoDB, Redis, and RabbitMQ running locally or with docker on their default port. For docker:

- install docker: [docker docs](https://docs.docker.com/engine/install/)
- run the mongodb container: `docker run -p 27017:27017 --name mongodb mongo:latest`
- run the redis container: `docker run -p 6379:6379 --name redisdb redis:latest`
- run the rabbitmq container: `docker run -p 5672:5672 --name rabbitmq rabbitmq:latest`
  &nbsp;

2. Run the client server:

- `cd client`
- `npm install`
- `npm run dev`  
  &nbsp;

3. In another terminal window, run the backend server:

- `cd server`
- Create .env file in the backend directory and add the following environment variables (DB\_\* env variables can be omitted if mongodb is running on the default settings and does not need authentication):
  - `SECRET_KEY={ value }` (set **value** to a secret key of your choosing)
  - `MODE={ dev | prod | test }`
- `poetry install`
- `poetry shell`
- `python3 main.py`  
  **NOTE**: check `.env.sample` or `app/settings/__init__.py` for all available environment variables  
  &nbsp;
  &nbsp;

4. Run the backend WITH docker compose:

- Ensure docker is installed
- `cd server`
- Ensure a .env file is created in the server directory with the required environment variables
- `docker compose up`

ENJOY!
