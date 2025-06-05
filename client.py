
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

class Serializer:
    @staticmethod
    def request_serializer(request: UserRequest) -> bytes:
        """Serialize Pydantic UserRequest object to JSON format"""
        return orjson.dumps(request.model_dump())

    @staticmethod
    def response_deserializer(data: bytes) -> UserListResponse:
        """Deserialize response from server to Pydantic UserListResponse object"""
        json_dict = orjson.loads(data)
        return UserListResponse(**json_dict)

    
class GreeterServiceStub:
    def __init__(self, client: dubbo.Client):
        self.unary = client.unary(
            method_name="unary",
            request_serializer=Serializer.request_serializer,
            response_deserializer=Serializer.response_deserializer
        )

    def say_hello(self, name: str, age: int) -> UserListResponse:
        """Create UserRequest object and send to server"""
        request = UserRequest(name=name, age=age)
        return self.unary(request)


if __name__ == "__main__":
    reference_config = ReferenceConfig.from_url("tri://127.0.0.1:50051/org.apache.dubbo.samples.serialization.json")
    dubbo_client = dubbo.Client(reference_config)

    stub = GreeterServiceStub(dubbo_client)
    result = stub.say_hello("dubbo-python", 18)
    
    print(f"Server response:")
    print(f"Greeting: {result.greeting}")
    print(f"Total users: {result.total_count}")
    print("Users:")
    for user in result.users:
        print(f"  - {user.name} ({user.email}), Age: {user.age}, Active: {user.is_active}")