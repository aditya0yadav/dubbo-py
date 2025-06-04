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
from pydantic import BaseModel
from typing import List, Optional
import dubbo
from dubbo.configs import ServiceConfig
from dubbo.proxy.handlers import RpcMethodHandler, RpcServiceHandler


def request_deserializer(data: bytes) -> dict:
    """Deserialize incoming request data from client"""
    return orjson.loads(data)


def response_serializer(message: str) -> bytes:
    """Serialize response message to send back to client"""
    return orjson.dumps({"message": message})


class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True


class UserListResponse(BaseModel):
    users: List[User]
    total_count: int


class UserServiceHandler:
    def __init__(self):
        # Fixed: Initialize users_db as instance variable
        self.users_db = [
            User(id=1, name="Alice", email="alice@example.com", age=30),
            User(id=2, name="Bob", email="bob@example.com", age=25),
        ]
    
    def list_users(self, request_data: dict) -> str:
        """
        Updated to accept the deserialized request data as a single dict parameter
        """
        name = request_data["name"]
        age = request_data["age"]
        
        # You can use the name and age parameters for filtering or processing
        user_list = [f"{user.name} ({user.age})" for user in self.users_db]
        return f"Hello {name} (age {age})! Users: {', '.join(user_list)}"


def build_service_handler():
    # build a method handler
    method_handler = RpcMethodHandler.unary(
        UserServiceHandler().list_users,
        method_name="unary",
        request_deserializer=request_deserializer,
        response_serializer=response_serializer,
    )
    # build a service handler
    service_handler = RpcServiceHandler(
        service_name="org.apache.dubbo.samples.serialization.json",
        method_handlers=[method_handler],
    )
    return service_handler


if __name__ == "__main__":
    # build server config
    service_handler = build_service_handler()
    service_config = ServiceConfig(service_handler=service_handler, host="127.0.0.1", port=50051)

    # start the server
    server = dubbo.Server(service_config).start()

    input("Press Enter to stop the server...\n")