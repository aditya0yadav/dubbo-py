from pydantic import BaseModel
from typing import List, Optional
import dubbo
from dubbo.configs import ServiceConfig
from dubbo.proxy.handlers import RpcMethodHandler, RpcServiceHandler
from dubbo.codec import DubboCodec

class UserRequest(BaseModel):
    name: str
    age: int

class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True

class UserListResponse(BaseModel):
    users: List[User]
    total_count: int
    greeting: str

def setup_codec(codec_type: str = 'json'):
    if codec_type == 'protobuf':
        pass
    else:
        request_deserializer, response_serializer = DubboCodec.get_serializer_deserializer(
            codec_type,
            UserRequest,
            UserListResponse
        )
        print(type(request_deserializer), type(response_serializer))
    return request_deserializer, response_serializer

class UserServiceHandler:
    def __init__(self):
        self.users_db = [
            User(id=1, name="Alice", email="alice@example.com", age=30),
            User(id=2, name="Bob", email="bob@example.com", age=25),
        ]
    
    def list_users(self, request: UserRequest) -> UserListResponse:
        greeting = f"Hello {request.name} (age {request.age})!"
        return UserListResponse(
            users=self.users_db,
            total_count=len(self.users_db),
            greeting=greeting
        )

def build_service_handler(codec_type: str = 'json'):
    method_handler = RpcMethodHandler.unary(
        UserServiceHandler().list_users,
        method_name="unary",
        codec_type="json",
        request_model = UserRequest,
        response_model = UserListResponse
    )
    service_handler = RpcServiceHandler(
        service_name="org.apache.dubbo.samples.serialization.json",
        method_handlers=[method_handler],
    )
    return service_handler

if __name__ == "__main__":
    CODEC_TYPE = 'json'
    service_handler = build_service_handler(CODEC_TYPE)
    service_config = ServiceConfig(service_handler=service_handler, host="127.0.0.1", port=50051)
    server = dubbo.Server(service_config).start()
    input(f"Server running with {CODEC_TYPE} codec. Press Enter to stop...\n")
