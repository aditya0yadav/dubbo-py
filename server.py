import orjson
from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import List, Optional, Dict, Any
import dubbo
from dubbo.configs import ServiceConfig
from dubbo.proxy.handlers import RpcMethodHandler, RpcServiceHandler
from dubbo.codec import DubboCodec
from datetime import datetime
import gzip
import base64

class UserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat() if value else None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip().title()

class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat() if value else None
    
    @field_serializer('metadata')
    def serialize_metadata(self, value: Dict[str, Any]) -> Dict[str, Any]:
        if not value:
            return {}
        return {k: str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v 
                for k, v in value.items()}

class UserListResponse(BaseModel):
    users: List[User]
    total_count: int
    greeting: str
    response_time: Optional[datetime] = Field(default_factory=datetime.now)
    api_version: str = Field(default="v1.0")
    
    @field_serializer('response_time')
    def serialize_response_time(self, value: datetime) -> str:
        return value.isoformat()
    
    def model_dump_custom(self, **kwargs) -> Dict[str, Any]:
        data = self.model_dump(**kwargs)
        data['summary'] = {
            'total_users': len(self.users),
            'active_users': sum(1 for user in self.users if user.is_active),
            'generated_at': self.response_time.isoformat()
        }
        return data

class SerializationStrategy:
    @staticmethod
    def serialize(obj: BaseModel) -> bytes:
        raise NotImplementedError
    
    @staticmethod
    def deserialize(data: bytes, model_class: type) -> BaseModel:
        raise NotImplementedError

class JSONStrategy(SerializationStrategy):
    @staticmethod
    def serialize(obj: BaseModel) -> bytes:
        if hasattr(obj, 'model_dump_custom'):
            return orjson.dumps(obj.model_dump_custom())
        return orjson.dumps(obj.model_dump())
    
    @staticmethod
    def deserialize(data: bytes, model_class: type) -> BaseModel:
        json_data = orjson.loads(data)
        return model_class(**json_data)

class CompressedJSONStrategy(SerializationStrategy):
    @staticmethod
    def serialize(obj: BaseModel) -> bytes:
        json_bytes = orjson.dumps(obj.model_dump())
        compressed = gzip.compress(json_bytes)
        return base64.b64encode(compressed)
    
    @staticmethod
    def deserialize(data: bytes, model_class: type) -> BaseModel:
        compressed_data = base64.b64decode(data)
        json_bytes = gzip.decompress(compressed_data)
        json_data = orjson.loads(json_bytes)
        return model_class(**json_data)

class PrettyJSONStrategy(SerializationStrategy):
    @staticmethod
    def serialize(obj: BaseModel) -> bytes:
        return orjson.dumps(
            obj.model_dump(), 
            option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
        )
    
    @staticmethod
    def deserialize(data: bytes, model_class: type) -> BaseModel:
        json_data = orjson.loads(data)
        return model_class(**json_data)

class CustomSerializer:
    def __init__(self, strategy: SerializationStrategy = None):
        self.strategy = strategy or JSONStrategy()
    
    def request_deserializer(self, data: bytes) -> UserRequest:
        try:
            return self.strategy.deserialize(data, UserRequest)
        except Exception as e:
            print(f"Deserialization error: {e}")
            json_data = orjson.loads(data)
            return UserRequest(**json_data)
    
    def response_serializer(self, response: UserListResponse) -> bytes:
        try:
            return self.strategy.serialize(response)
        except Exception as e:
            print(f"Serialization error: {e}")
            return orjson.dumps(response.model_dump())

DubboCodec.init('json', model_type=UserListResponse)
codec_instance = DubboCodec.get_instance()

serializer = CustomSerializer(PrettyJSONStrategy())

def request_deserializer(data: bytes) -> UserRequest:
    return serializer.request_deserializer(data)

def response_serializer(response: UserListResponse) -> bytes:
    return serializer.response_serializer(response)

class UserServiceHandler:
    def __init__(self):
        self.users_db = [
            User(
                id=1, 
                name="Alice", 
                email="alice@example.com", 
                age=30,
                metadata={"role": "admin", "last_login": datetime.now()}
            ),
            User(
                id=2, 
                name="Bob", 
                email="bob@example.com", 
                age=25,
                metadata={"role": "user", "preferences": {"theme": "dark"}}
            ),
        ]
    
    def list_users(self, request: UserRequest) -> UserListResponse:
        greeting = f"Hello {request.name} (age {request.age})! Request received at {request.timestamp}"
        response = UserListResponse(
            users=self.users_db,
            total_count=len(self.users_db),
            greeting=greeting
        )
        print("List Type User", type(response))
        print(f"Serialized response preview: {orjson.dumps(response.model_dump())[:200]}...")
        return response

def build_service_handler():
    method_handler = RpcMethodHandler.unary(
        UserServiceHandler().list_users,
        method_name="unary",
        request_deserializer=request_deserializer,
        response_serializer=response_serializer,
    )
    service_handler = RpcServiceHandler(
        service_name="org.apache.dubbo.samples.serialization.json",
        method_handlers=[method_handler],
    )
    return service_handler

if __name__ == "__main__":
    service_handler = build_service_handler()
    service_config = ServiceConfig(service_handler=service_handler, host="127.0.0.1", port=50051)
    server = dubbo.Server(service_config).start()
    input("Press Enter to stop the server...\n")
