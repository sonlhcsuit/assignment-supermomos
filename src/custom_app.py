from fastapi import FastAPI

from src.container import Container


class CustomAPIApp(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._container = None

    # Set container
    @property
    def container(self):
        return self._container

    @container.setter
    def container(self, container: Container):
        self._container = container

    def full_config_reset(self):
        self._container.config_service.reset()
