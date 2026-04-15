from __future__ import annotations

from app.bootstrap import create_application, create_main_window
from services.runtime_logging import configure_runtime_logging, install_global_exception_hooks


def main() -> int:
    configure_runtime_logging()
    install_global_exception_hooks()
    app = create_application()
    window = create_main_window()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
