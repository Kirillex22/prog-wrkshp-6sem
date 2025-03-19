import grpc
from UserService import user_pb2
from UserService import user_pb2_grpc

class UserServiceClient:
    def __init__(self, address='localhost:50051'):
        self.channel = grpc.insecure_channel(address)
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)


    def createGetUserRequest(self):
        return user_pb2.GetUserRequest()


