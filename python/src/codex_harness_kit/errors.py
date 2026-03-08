class ProtocolError(Exception):
    pass


class JsonRpcCodecError(ProtocolError):
    pass


class ProtocolStreamError(ProtocolError):
    pass


class TransportClosedError(ProtocolError):
    pass
