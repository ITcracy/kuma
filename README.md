# Kuma.

**WIP**

### Run example


- Install dependencies using `poetry`
- Migrate using `alembic upgrade head`
- run server using
```sh
uvicorn app.backend.main:app --reload
```
- Navigate to `http://127.0.0.1:8000/api/pandaui/`
- First box should be the module of variable, `df` or `pd`
- Second box is the function like read_csv
- Third box is for positional args
