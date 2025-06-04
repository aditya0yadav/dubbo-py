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
        # Fixed: Use correct serializer methods that match the server
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


# FIXES MADE:
# 1. Changed client request_serializer to use orjson.dumps() with dict format to match server expectations
# 2. Changed client response_deserializer to parse JSON response from server
# 3. Server method now accepts name and age parameters as expected
# 4. Fixed server's users_db reference issue by making it an instance variable
# 5. Server method now returns a simple string message instead of complex object