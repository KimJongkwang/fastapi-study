import typing
from starlette.types import ASGIApp
from starlette.middleware.trustedhost import TrustedHostMiddleware, ENFORCE_DOMAIN_WILDCARD


class AddExceptPathTHM(TrustedHostMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        allowed_hosts: typing.Sequence[str] = None,
        except_path: typing.Sequence[str] = None,
        www_redirect: bool = True,
    ) -> None:
        super().__init__(app, allowed_hosts, www_redirect)
        if except_path is None:
            except_path = []
