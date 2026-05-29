from fastapi import FastAPI

app = FastAPI(title="Research Reconstruction API")


@app.get("/")
def read_root():
    return {"status":"Environment is successfully configured!", "system":"Online"}
