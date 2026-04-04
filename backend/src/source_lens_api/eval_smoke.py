from .config import get_settings
from .main import create_app


def main() -> None:
    settings = get_settings()
    app = create_app()
    print(f"eval scaffold ready: {settings.app_name} [{settings.environment}]")
    print(f"registered routes: {len(app.routes)}")


if __name__ == "__main__":
    main()

