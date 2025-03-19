import json
import atexit
import grpc
from concurrent import futures
import user_pb2
import jwt
import os
import user_pb2_grpc
import bcrypt
from datetime import datetime, timedelta, timezone
from google.protobuf.json_format import MessageToDict
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
users = None
path = 'UserService/users.json'

with open(path, 'r') as f:
    serialized = f.read()
    users = {int(k): v for k, v in json.loads(serialized).items()}

def get_base():
    with open('UserService/last_generated_id', 'r') as f:
        base = int(f.read())
        return base

base = get_base()

def generate_id():
    global base
    while True:
        base += 1
        yield base

def dump():
    with open(path, 'w') as f:
        serialized = json.dumps(users)
        print(serialized)
        f.write(serialized)

    with open('UserService/last_generated_id', 'w') as f:
        f.write(str(base))

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

id_generator = generate_id()

def add_user(user):
    userid = next(id_generator)
    user.password = hash_password(user.password)
    users[userid] = MessageToDict(user)
    return userid

def find_user(login):
    return next(((id, user) for id, user in users.items() if user.get("login") == login), None)

def verify(auth_request):
    if not find_user(auth_request.login):
        return None

    userid, user = find_user(auth_request.login)
    try:
        if check_password(auth_request.password, user.get("password")):
            return userid
        return None
    except:
        return None


class UserService(user_pb2_grpc.UserServiceServicer):
    def Register(self, request, context):
        if find_user(request.login):
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('User already exists')
            return user_pb2.RegisterResponse()

        id = add_user(request)
        return user_pb2.RegisterResponse(userid = id)


    def Auth(self, request, context):
        userid = verify(request)
        if not userid:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('User not found')
            return user_pb2.AuthResponse()

        payload = {
            "userid": userid,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return user_pb2.AuthResponse(token=token)


    def GetUser(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        if not token or not token.startswith("Bearer "):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Missing or invalid token")
            return user_pb2.GetUserResponse()

        try:
            decoded_token = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
            userid = int(decoded_token["userid"])
            user = users.get(userid, None)
            if not user:
                raise jwt.InvalidTokenError()

            return user_pb2.GetUserResponse(userid=userid, full_name = user.get("full_name"))
        except jwt.ExpiredSignatureError:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Token expired")
            return user_pb2.GetUserInfoResponse()
        except jwt.InvalidTokenError:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid token")
            return user_pb2.GetUserInfoResponse()

def save():
    dump()

def serve():
    port = os.getenv("USER_SERVICE_PORT")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port(f"[::]:{port}")
    atexit.register(save)
    server.start()
    print(f"Server is running on port {port}...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()