docker run -d \
  --name postgres_container \
  --network my_bridge \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassw0rd \
  -e POSTGRES_DB=mydb \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:latest
