from abc import ABC, abstractmethod
from typing import Any, Type, Protocol, Callable, TypeVar, Generic
import dubbo
from functools import wraps
from pydantic import BaseModel


class Codec(ABC):
    """Abstract base class for all codecs"""
    
    @abstractmethod
    def encode(self, data: Any) -> bytes:
        """Encode data into bytes"""
        pass

    @abstractmethod
    def decode(self, data: bytes) -> Any:
        """Decode bytes into original data"""
        pass


class EncodingFunction(Protocol):
    def __call__(self, obj: Any) -> bytes: ...


class DecodingFunction(Protocol):
    def __call__(self, data: bytes) -> Any: ...


ModelT = TypeVar('ModelT', bound=BaseModel)


class JsonCodec(Codec, Generic[ModelT]):
    """Codec implementation for JSON and Pydantic models"""
    
    def __init__(self, model_type: Type[ModelT]):
        self.model_type = model_type

    def encode(self, data: Any) -> bytes:
        if isinstance(data, dict):
            data = self.model_type(**data)
        elif not isinstance(data, self.model_type):
            raise TypeError(f"Expected {self.model_type.__name__} or dict, got {type(data).__name__}")
        return data.model_dump_json().encode('utf-8')

    def decode(self, data: bytes) -> ModelT:
        return self.model_type.model_validate_json(data.decode('utf-8'))

    @classmethod
    def create_encoder(cls, model_type: Type[ModelT]) -> EncodingFunction:
        codec = cls(model_type)
        return codec.encode

    @classmethod
    def create_decoder(cls, model_type: Type[ModelT]) -> DecodingFunction:
        codec = cls(model_type)
        return codec.decode
