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
from grpc import ServerInterceptor

# ----------------------------------------------------
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
users = None
path = 'UserService/users.json'
DEFAULT_ROLE = os.getenv("DEFAULT_ROLE")
ADMIN_ROLE = os.getenv("ADMIN_ROLE")
EXCLUDED_METHODS = {
    "/user.UserService/Auth",
    "/user.UserService/Register"
}

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
    dict_user_model = MessageToDict(user)
    dict_user_model['role'] = DEFAULT_ROLE
    users[userid] = dict_user_model
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

def get_user_from_token(token):
    decoded_token = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
    userid = int(decoded_token["userid"])
    user = users.get(userid, None)
    if not user:
        raise jwt.InvalidTokenError()

    return {'userid': userid, 'user': user}


def switch_user_role(userid, role):
    user = users.get(userid, None)
    user['role'] = role
    return user

def startup():
    if not users.get(1, None):
        users[1] = {
            'login': 'admin',
            'password': hash_password('admin'),
            'full_name': 'ADMIN_ACCOUNT',
            'role': ADMIN_ROLE
        }

# ----------------------------------------------------

startup()

# ----------------------------------------------------

class AuthInterceptor(ServerInterceptor):

    def _unauth(self, message):
        def deny(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, message)

        return grpc.unary_unary_rpc_method_handler(deny)

    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method

        if method in EXCLUDED_METHODS:
            return continuation(handler_call_details)

        metadata = dict(handler_call_details.invocation_metadata)

        print(f"[gRPC] Вызов метода: {method}")
        print(f"[gRPC] Метаданные: {metadata}")

        token = metadata.get('authorization')

        if not token:
            context = grpc.ServicerContext()
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Missing token')
        try:
            jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            return self._unauth("Token has expired")

        except jwt.InvalidTokenError:
            return self._unauth("Invalid token")

        return continuation(handler_call_details)


class UserService(user_pb2_grpc.UserServiceServicer):
    def Register(self, request, context):
        if find_user(request.login):
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('User already exists')
            return user_pb2.RegisterResponse()

        userid = add_user(request)
        return user_pb2.RegisterResponse(userid = userid, role = DEFAULT_ROLE)


    def Auth(self, request, context):
        userid = verify(request)
        if not userid:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('User not found')
            return user_pb2.AuthResponse()

        payload = {
            "userid": userid,
            "role": users[userid].get("role", None),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return user_pb2.AuthResponse(token=token)


    def GetUser(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        item = get_user_from_token(token)
        userid, user = item['userid'], item['user']

        return user_pb2.GetUserResponse(
            userid=userid,
            full_name = user.get("full_name", None),
            login = user.get("login", None),
            role = user.get("role", None)
        )

    def SetRole(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        user = get_user_from_token(token)['user']

        try:
            if user.get('role', None) == ADMIN_ROLE:
                target_userid, target_role = request.userid, request.role
                user = switch_user_role(target_userid, target_role)
                return user_pb2.SetRoleResponse(userid = target_userid, role = user['role'])
        except:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('User not found')
            return user_pb2.SetRoleResponse()


    def GetUsersList(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        user = get_user_from_token(token)['user']

        if user.get('role', None) != ADMIN_ROLE:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('User is not an admin')
            return user_pb2.GetUsersResponse()

        selected_users = []
        for userid, user in users.items():
            selected_users.append(
            user_pb2.GetUserResponse(
                userid=userid,
                full_name=user.get("full_name", None),
                login=user.get("login", None),
                role=user.get("role", None)
            ))

        return user_pb2.GetUsersListResponse(users=selected_users)


def save():
    dump()

def serve():
    port = os.getenv("USER_SERVICE_PORT")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors = [AuthInterceptor()])
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port(f"[::]:{port}")
    atexit.register(save)
    server.start()
    print(f"Server is running on port {port}...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()