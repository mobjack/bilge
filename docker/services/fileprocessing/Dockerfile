FROM debian:bullseye-slim

#RUN apk add --update \
RUN apt-get update
RUN apt-get install -y \
    samba \
    g++ \
    python3 \
    python3-pip \
    python3-venv && apt-get clean

EXPOSE 445/tcp

COPY entrypoint.sh smb.conf /
COPY file_processing/ /file_processing
RUN mkdir -p /data/db /data/smb


# Python
ENV VIRTUAL_ENV=/file_processing/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV_/bin:$PATH"
RUN pip install -r /file_processing/bin/requirements.txt

#ENTRYPOINT ["smbd", "--foreground", "--debug-stdout", "--debuglevel=1"]
ENTRYPOINT ["/entrypoint.sh"]
CMD ["smbd"]
