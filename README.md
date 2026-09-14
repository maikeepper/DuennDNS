# Dev

## activate environment
```
source venv/bin/activate
```

## install new stuff
```
source venv/bin/activate
pip install stuff
```

## create requirements
```
pip freeze > requirements.txt
```

# Server
```
docker-compose build; docker-compose down; docker-compose up -d
docker logs -f www2
tail -f logs/duennDns.log 
```

# Client request
Basic Authorization siehe app.py
```
GET https://www.contio.eu/nic/update?myip=123.45.678.9
```

# Key ersetzen
- Key in Postman testen (LIST_ID_URLS + Bearer Token im Authorization Header)
- Key in app.py ersetzen
```
docker stop www2
docker build www2
docker compose up -d
```
