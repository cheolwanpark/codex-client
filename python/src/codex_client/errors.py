class ProtocolError(Exception):
    pass


class JsonRpcCodecError(ProtocolError):
    pass


class ProtocolStreamError(ProtocolError):
    pass


class TransportClosedError(ProtocolError):
    pass


class ProtocolClientError(ProtocolError):
    pass


class RequestTimeoutError(ProtocolClientError):
    pass


class ClientClosedError(ProtocolClientError):
    pass


class UnknownResponseIdError(ProtocolClientError):
    pass


class MiddlewareAbortedError(ProtocolClientError):
    pass
