import orjson
import dubbo
from dubbo.configs import ReferenceConfig
from pydantic import BaseModel
from typing import List, Optional

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

# Simple serialization functions
def pydantic_to_json(pydantic_obj: BaseModel) -> bytes:
    """Convert Pydantic object to JSON bytes"""
    return orjson.dumps(pydantic_obj.model_dump())

def json_to_pydantic(json_data: bytes, model_class: type) -> BaseModel:
    """Convert JSON bytes to Pydantic object"""
    data = orjson.loads(json_data)
    return model_class(**data)

class Serializer:
    @staticmethod
    def request_serializer(request: UserRequest) -> bytes:
        return pydantic_to_json(request)

    @staticmethod
    def response_deserializer(data: bytes) -> UserListResponse:
        return json_to_pydantic(data, UserListResponse)

class GreeterServiceStub:
    def __init__(self, client: dubbo.Client):
        self.unary = client.unary(
            method_name="unary",
            request_serializer=Serializer.request_serializer,
            response_deserializer=Serializer.response_deserializer
        )

    def say_hello(self, name: str, age: int) -> UserListResponse:
        request = UserRequest(name=name, age=age)
        return self.unary(request)

if __name__ == "__main__":
    reference_config = ReferenceConfig.from_url("tri://127.0.0.1:50051/org.apache.dubbo.samples.serialization.json")
    dubbo_client = dubbo.Client(reference_config)

    stub = GreeterServiceStub(dubbo_client)
    result = stub.say_hello("dubbo-python", 18)
    
    print(f"Greeting: {result.greeting}")
    print(f"Total users: {result.total_count}")
    for user in result.users:
        print(f"  - {user.name} ({user.email}), Age: {user.age}")