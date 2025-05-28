FROM python:3.10-slim

WORKDIR /app
COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN ls -la /app/data/check-covid/llm-judge-screening/ || echo "Data directory missing!"

EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["python", "run_consultancy_gradio.py"]

# docker build -t consult .
# docker run -p 7860:7860 consult