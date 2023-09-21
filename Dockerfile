FROM osgeo/gdal:ubuntu-small-latest

RUN apt-get update && apt-get -y install python3-pip --fix-missing

WORKDIR /work-pre-flood

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

#ต้องมีการแบ่งด้วย (,) เพราะ CMD ไม่สามารถอ่าน (space) ได้
# CMD ["python3", "./app/LS_v2.py"]