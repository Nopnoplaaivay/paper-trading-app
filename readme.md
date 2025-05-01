python api_server.py -a src.app:app -p 8000 -w 2
streamlit run web_ui.py

docker build -t trading-app-backend -f Dockerfile.backend .
docker run --name trading-app-container -d -p 4000:8000 trading-app-backend "-a=backend:app" "-w=2"

docker build -t dnse-realtime-data -f Dockerfile.realtime_data .
docker run --name dnse-realtime-data-container -d dnse-realtime-data