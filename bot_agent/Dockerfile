FROM python:3.9-slim
WORKDIR /app
RUN pip install requests aiohttp aiohttp-socks
COPY agent.py .
CMD ["python", "agent.py"]