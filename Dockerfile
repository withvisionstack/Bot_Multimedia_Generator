FROM  python:3.14.3

WORKDIR /Image_Generator_bot

COPY requeriments.txt .

RUN pip install --no-cache-dir -r requeriments.txt

COPY . .

CMD ["python", "main.py"]