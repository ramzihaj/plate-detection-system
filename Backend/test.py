from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    try:
        return {"message": "Hello World"}
    except Exception as e:
        return {"error": str(e)}
