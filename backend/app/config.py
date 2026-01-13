import os

class Config:
	SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
	DB_USER = os.environ.get("POSTGRES_USER", "postgres")
	DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
	DB_HOST = os.environ.get("POSTGRES_HOST", "db")
	DB_NAME = os.environ.get("POSTGRES_DB", "portfolio")
	SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
		f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
	)
	SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
