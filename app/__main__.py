if __name__ == "__main__":
    import uvicorn as uvicorn

    from app.container import Container, AppConfig
    from app.services import messagebus
    from fastapi import FastAPI

    from app.presentation.router import router

    container = Container()
    container.config.from_pydantic(AppConfig())
    container.wire([messagebus])

    app = FastAPI()
    app.include_router(router)
    app.container = container
    uvicorn.run(app, host="0.0.0.0")
