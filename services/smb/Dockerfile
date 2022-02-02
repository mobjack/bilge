FROM python:slim-bullseye

ENV VIRTUAL_ENV=/fastapi/venv

COPY entrypoint.sh smb.conf /
COPY /fastapi /fastapi

RUN apt-get update \
    && apt-get install -y samba \
    && mkdir -p /data/smb \
    && python3 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m pip install --upgrade pip \
    && pip3 install -r /fastapi/bin/requirements.txt

EXPOSE 445/tcp
EXPOSE 8080/tcp

ENTRYPOINT ["/entrypoint.sh"]
CMD ["smbd"]
