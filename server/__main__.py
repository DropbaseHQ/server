from uvicorn import run

if __name__ == "__main__":
    run("server.main:app", host="0.0.0.0", port=9000, reload=True)
