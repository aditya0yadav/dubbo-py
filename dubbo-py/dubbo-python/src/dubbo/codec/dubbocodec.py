from abc import ABC, abstractmethod
from typing import Any, Type, Optional
from .codec import Codec
from .CodecRegistry import CodecRegistry
from pydantic import BaseModel

class DubboCodec:
    _codec_instance: Optional[Codec] = None

    @staticmethod
    def init(codec_type: str = 'json', model_type: Optional[Type[BaseModel]] = None, **codec_kwargs):
        if codec_type == 'json' and model_type is None:
            raise ValueError("model_type is required when using JsonCodec")
        DubboCodec._codec_instance = CodecRegistry.get_codec(codec_type, model_type=model_type, **codec_kwargs)

    @staticmethod
    def get_instance() -> Codec:
        if DubboCodec._codec_instance is None:
            raise RuntimeError("DubboCodec is not initialized. Call DubboCodec.init(...) first.")
        return DubboCodec._codec_instance

    @staticmethod
    def encode(data: Any) -> bytes:
        return DubboCodec.get_instance().encode(data)

    @staticmethod
    def decode(data: bytes) -> Any:
        return DubboCodec.get_instance().decode(data)
