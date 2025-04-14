#!/bin/bash

echo "🔐 Creating music_reader role..."
curl -k -u elastic:$ELASTIC_PASSWORD \
  -X PUT http://localhost:9200/_security/role/music_reader \
  -H "Content-Type: application/json" \
  -d '{
    "indices": [
      {
        "names": [ "musicxml" ],
        "privileges": [ "read", "view_index_metadata" ]
      }
    ]
  }'

echo "👤 Creating kibanabot user..."
curl -k -u elastic:$ELASTIC_PASSWORD \
  -X PUT http://localhost:9200/_security/user/kibanabot \
  -H "Content-Type: application/json" \
  -d "{
    \"password\": \"$APP_ES_PASSWORD\",
    \"roles\": [\"kibana_system\", \"music_reader\"],
    \"full_name\": \"Kibana Bot User\"
  }"

echo "📦 Indexing musicxml data..."
curl -k -u elastic:$ELASTIC_PASSWORD \
  -X POST http://localhost:9200/musicxml/_bulk \
  -H "Content-Type: application/json" \
  --data-binary @data/bulk_music.json

echo "✅ Setup complete!"
