FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN python -m pip install --user -r requirements.txt

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./api /code/api

RUN python ./api/download_checkpoints.py

ENV PATH "$PATH:/root/.local/bin"

CMD ["uvicorn", "api.api:api", "--host", "0.0.0.0", "--port", "80", "--log-level", "trace"]
