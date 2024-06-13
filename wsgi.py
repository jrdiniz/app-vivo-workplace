from app import create_app
from app.extensions import socket

app = create_app()

if __name__ == "__main__":
    socket.init_app(app)
    socket.socketio.run(app)
