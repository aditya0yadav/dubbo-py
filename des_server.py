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

from pydantic import BaseModel
from typing import List, Optional
from dubbo.configs import ServiceConfig
from dubbo.proxy.handlers import RpcMethodHandler, RpcServiceHandler
from dubbo.codec import DubboCodec
import dubbo

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
    def list_users(self) -> UserListResponse:
        users_db = [
            User(id=1, name="Alice", email="alice@example.com", age=30),
            User(id=2, name="Bob", email="bob@example.com", age=25),
        ]
        return UserListResponse(
            users=self.users_db,
            total_count=len(self.users_db)
        )

def create_serializers():
    
    DubboCodec.init('json', model_type=UserListResponse)
    codec_instance = DubboCodec.get_instance()
    print("codec_instance",type(codec_instance.decode))
    return {
        'user_list_serializer': codec_instance.encode,
        'empty_deserializer': codec_instance.decode,
    }

def build_service_handler():
    serializers = create_serializers()
    print("build service handler",type(serializers['user_list_serializer']))
    method_handler = RpcMethodHandler.unary(
        UserServiceHandler().list_users,
        method_name="unary",
        request_deserializer=serializers['empty_deserializer'],
        response_serializer=serializers['user_list_serializer'],
    )
    print(type(method_handler))
    service_handler =  RpcServiceHandler(
        service_name="org.apache.dubbo.samples.serialization.json",
        method_handlers=[method_handler],
    )
    print(type(service_handler))
    return service_handler


if __name__ == "__main__":
    service_handler = build_service_handler()
    service_config = ServiceConfig(service_handler=service_handler, host="127.0.0.1", port=50051)

    server = dubbo.Server(service_config).start()
