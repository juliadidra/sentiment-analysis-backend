# main.py
import os
import googleapiclient.discovery
from pydantic import BaseModel
from LeIA import SentimentIntensityAnalyzer as Leiaanalise
from pathlib import Path
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as Vaderanalise

class Link(BaseModel):
    codigo: str
    lang: str
    

from fastapi import FastAPI
app = FastAPI()
@app.get("/")
async def root():
 return {"greeting":"Hello world"}


@app.post("/analisar")
async def analysingVideo(link: Link):
    print(link.codigo)
    print(link.lang)

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    BASE_DIR = Path(__file__).resolve().parent.parent

    dotenvpath = os.path.join(BASE_DIR, '.env')
    load_dotenv(dotenvpath)

    key = os.environ.get("DEVELOPER_KEY")
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = key)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        moderationStatus="published",
        order="orderUnspecified",
        videoId=link.codigo
    )

    lista_comentarios = None

    if(link.lang == "en"):

        try:
            lista_comentarios = request.execute()
        except Exception as e:
            print(e)
            return { "error": e }
        
        analyser = Vaderanalise()

        data = []
    
        for comentario_dict in lista_comentarios["items"]:
            comentario = comentario_dict["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            score = analyser.polarity_scores([comentario])['compound']

            data.append({
            'commentary': comentario,
            'score': score
            })
        
        return data
        # print(lista_comentarios["items"][0]["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
    elif(link.lang == "pt"):
        try:
            lista_comentarios = request.execute()
        except Exception as e:
            print(e)
            return { "error": e }

        analise = Leiaanalise()

        data = []
    
        for comentario_dict in lista_comentarios["items"]:
            comentario = comentario_dict["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            score = analise.polarity_scores(comentario)['compound']

            data.append({
            'commentary': comentario,
            'score': score
            })
        
        return data

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='localhost', port=8000, log_level='info', reload=True)