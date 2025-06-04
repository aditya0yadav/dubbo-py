# Fixed Dubbo Client to match server serialization

import orjson
import dubbo
from dubbo.configs import ReferenceConfig


class Serializer:
    @staticmethod
    def request_serializer(name: str, age: int) -> bytes:
        """Serialize request data (name, age) to JSON format to match server expectations"""
        return orjson.dumps({"name": name, "age": age})

    @staticmethod
    def response_deserializer(data: bytes) -> str:
        """Deserialize response from server (JSON format)"""
        json_dict = orjson.loads(data)
        return json_dict["message"]

    
class GreeterServiceStub:
    def __init__(self, client: dubbo.Client):
        self.unary = client.unary(
            method_name="unary",
            request_serializer=Serializer.request_serializer,
            response_deserializer=Serializer.response_deserializer
        )

    def say_hello(self, name: str, age: int):
        return self.unary(name, age)


if __name__ == "__main__":
    reference_config = ReferenceConfig.from_url("tri://127.0.0.1:50051/org.apache.dubbo.samples.serialization.json")
    dubbo_client = dubbo.Client(reference_config)

    stub = GreeterServiceStub(dubbo_client)
    result = stub.say_hello("dubbo-python", 18)
    print(f"Server response: {result}")

