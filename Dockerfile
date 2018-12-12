FROM python:3.7-slim
RUN apt-get update && apt-get install -y \
	poppler-utils \
	libglib2.0-0 \
	&& rm -rf /var/lib/apt/lists/*
COPY . /app
RUN pip3 install -r /app/requirements.txt
ENTRYPOINT ["/bin/sh"]
