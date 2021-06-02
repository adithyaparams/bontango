from fastapi import FastAPI, Depends
from endpoints import users, auth, google, senders, articles

app = FastAPI()

app.include_router(google.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(senders.router)
app.include_router(articles.router)