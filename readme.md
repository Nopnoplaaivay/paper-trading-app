python api_server.py -a src.app:app -p 8000 -w 2
streamlit run client.py

docker build -t trading-app-backend -f docker/Dockerfile.backend .
docker run --name trading-app-container -d -p 4000:8000 trading-app-backend "-a=server:app" "-w=2"

docker build -t dnse-realtime-data -f docker/Dockerfile.realtime_data .
docker run --name dnse-realtime-data-container -d dnse-realtime-data