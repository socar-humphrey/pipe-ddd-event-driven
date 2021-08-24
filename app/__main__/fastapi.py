from app.__main__ import app
from app.presentation.router import router

app.include_router(router)
