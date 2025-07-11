FROM python:3.12-bookworm


WORKDIR /torznab_indexes_api
ENV PYTHONPATH="/torznab_indexes_api"

RUN pip install --upgrade pip
# RUN pip install playwright==1.47.0 && playwright install --with-deps chromium

COPY requirements/*.txt ./requirements/

RUN pip install -r requirements/base.txt

COPY ./ .

ENTRYPOINT ["python", "torznab_indexes_api/main.py"]