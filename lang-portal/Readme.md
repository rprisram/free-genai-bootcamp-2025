## Install

```sh
pip install -r requirements.txt
```

## Setup DB

```
invoke init-db
```

## OR Run

```sh
#python app.py
python tasks.py init-db
python tasks.py migrate
python tasks.py seed
```
```
### Execute in backend-fastapi directory otherwise words.db wont be found
uvicorn lang-portal.backend-fastapi.app.main:app --host 127.0.0.1 --port 5000
```

## FE Execution

```sh
npm i   
npm run dev
```