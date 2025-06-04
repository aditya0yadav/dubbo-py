class Serializer:
    @staticmethod
    def request_serializer(name: str, age: int) -> bytes:
        """Serialize request data (name, age) to binary format"""
        return f"{name},{age}".encode('utf-8')

    @staticmethod
    def response_deserializer(data: bytes) -> str:
        """Deserialize response binary data to message string"""
        return data.decode('utf-8')

    @staticmethod
    def request_deserializer(data: bytes) -> tuple[str, int]:
        """Deserialize request binary data to name and age"""
        decoded = data.decode('utf-8')
        name, age_str = decoded.split(',', 1)
        return name, int(age_str)

    @staticmethod
    def response_serializer(message: str) -> bytes:
        """Serialize response message to binary format"""
        return message.encode('utf-8')