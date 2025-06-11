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

def request_serializer(name: str, age: int) -> bytes:
    return orjson.dumps({"name": name, "age": age})

def response_deserializer(data: bytes) -> str:
    json_dict = orjson.loads(data)
    return json_dict["message"]


class UserListResponse(BaseModel):
    users: List[User]
    total_count: int
    greeting: str

class GreeterServiceStub:
    def __init__(self, client: dubbo.Client):
        self.unary = client.unary(
            method_name="unary",
            codec_type="json",
            request_model = UserListResponse,
            response_model = UserRequest
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