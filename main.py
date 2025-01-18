from models import FilmModel, engine
from sqlalchemy.orm import Session
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel


app = FastAPI()

@app.get('/films')
def all_films():
    with Session(engine, autoflush=False) as db:

        films = db.query(FilmModel).all()
        
        if films is not None:
            return {"films": films}
        
        return {'films': 'пусто'}
        
    

@app.get('/films/{film_id}')
def detail_film(film_id: int):
    with Session(engine, autoflush=False) as db:

        film = db.get(FilmModel, film_id)

        if film is not None:
            return {'id': film.id, 'name': film.name}
        
        return {'detail': 'фильма нет'}
        

           


class FilmScheme(BaseModel):
    name: str


@app.post('/films/add_new')
def add_new(new_film : FilmScheme):
    with Session(engine, autoflush=False) as db:

        db.add(FilmModel(
            name = new_film.name 
        ))
        db.commit()

        return {'name': new_film.name}
    

        
if __name__ == '__main__':

    uvicorn.run('main:app', 
                host="127.0.0.1", 
                port=80, 
                reload=True)
    

