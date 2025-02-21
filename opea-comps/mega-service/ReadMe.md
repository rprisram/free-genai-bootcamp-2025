## Download (Pull) a model

curl -X POST http://localhost:8000/v1/example-service -H "Content-Type: application/json" -d '{
  "messages": [
    {"role": "user", "content": "Why is the sky blue?"}
  ]
}'