from fastapi import FastAPI
from fastapi_socketio import SocketManager
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

class Data:
    data = {
        'calisan': ['Ahmet Yilmaz', 'Can Erturk', 'Hasan Korkmaz', 'Cenk Saymaz', 'Ali Turan', 'Riza Erturk', 'Mustafa Can'],
        'Departman': ['Insan Kaynaklari', 'Bilgi Islem', 'Muhasebe', 'Insan Kaynaklari', 'Bilgi Islem', 'Muhasebe', 'Bilgi Islem'],
        'Yas': [30, 25, 45, 50, 23, 34, 42],
        'Semt': ['Kadikoy', 'Tuzla', 'Maltepe', 'Tuzla', 'Kadikoy', 'Tuzla', 'Maltepe'],
        'Maas': [5000, 3000, 4000, 3500, 2750, 6500, 4500]
    }

app = FastAPI()
sio = SocketManager(app=app)

@app.get("/")
async def main():
    return {"message": "Hello World"}

@sio.on('join')
async def handle_join(sid, *args, **kwargs):
    print("Baglanti gerceklesti...")
    await sio.emit('lobby', 'User joined')

def process_data(data):
    data = data.to_json(orient='records')
    data = data.replace('[','').replace(']','').replace('"','').replace(',','\n')
    data = data.split('\n')
    return data

@sio.on('maas')
async def test(sid,*args, **kwargs):
    maas = Data.data['Maas']
    await sio.emit('maas', [data])

@sio.on('isim')
async def test(sid,*args, **kwargs):
    data = Data.data['calisan']
    maas = Data.data['Maas']
    await sio.emit('isim', [data, maas])



@sio.on('rastgeleCalisanCek')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    data = df.sample(1)
    data = data.to_json(orient='records')
    await sio.emit('rastgeleCalisanCek', data)

@sio.on('semtlereGoreCalisanIsimleri')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    data = df.groupby('Semt').get_group('Kadikoy')['calisan']
    data = data.to_json(orient='records')
    await sio.emit('semtlereGoreCalisanIsimleri', data)

@sio.on('departmanlarinBilgileri')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Departman').get_group('Bilgi Islem')
    result = result.to_json(orient='records')
    await sio.emit('departmanlarinBilgileri', result)

@sio.on('departmanlarinToplamMaaslari')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Departman')["Maas"].sum()
    result = result.to_json(orient='records')
    await sio.emit('departmanlarinToplamMaaslari', result)

@sio.on('departmanlarinOrtalamaMaaslari')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Departman')["Maas"].mean()
    result = result.to_json(orient='records')
    await sio.emit('departmanlarinOrtalamaMaaslari', result)

@sio.on('departmanlarinEnDusukMaasVeYas')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Departman').min()[['Maas','Yas']]
    result = result.to_json(orient='records')
    await sio.emit('departmanlarinEnDusukMaasVeYas', result)

@sio.on('departmandakiOrtalamaYas')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Departman')['Yas'].mean()
    result = result.to_json(orient='records')
    await sio.emit('departmandakiOrtalamaYas', result)

@sio.on('semtlerdekiCalisanSayilari')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Semt')['calisan'].count()
    result = result.to_json(orient='records')
    await sio.emit('semtlerdekiCalisanSayilari', result)

@sio.on('semtlerdekiKadikoydekiCalisanSayisi')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Semt').get_group('Kadikoy')['calisan'].count()
    # result = result.to_json(orient='records')
    await sio.emit('semtlerdekiKadikoydekiCalisanSayisi', str(result))
    

if __name__ == '__main__':
    import logging
    import sys

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    
    import uvicorn

    uvicorn.run("socket_handlers:app", host='localhost', port=8081, reload=True)


# ---------------------------------------------------------

# result = df.groupby('Semt').get_group('Kadıköy')['Çalışan'] Semtlerden Kadıköyde oturan çalışanların adları.
# result = df.groupby('Departman').get_group('Bilgi İşlem') Departmanlardan 'Bilgi İşlem' bilgilerini getirir.
# result = df.groupby('Departman').sum() Departmandaki sayısal değerleri toplar.
# result = df.groupby('Departman').mean() Departmandaki sayısal değerlerin ortalamasını alır.
# result = df.groupby('Departman').min()[['Maaş','Yaş']]
# result = df.groupby('Semt')['Yaş'].mean()
# result = df.groupby('Semt')['Çalışan'].count() Semtlere göre çalışan sayılarını gösterir.
# result = df.groupby('Semt').get_group('Kadıköy')['Çalışan'].count() Semtlerden, Kadıköy'de çalışan sayısını gösterir.