# Bypass certificate validation for self-signed certificates:
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }

# Define environment variables if needed
$ELASTIC_PASSWORD = "your_elastic_password"
$APP_ES_PASSWORD = "your_app_es_password"

Write-Output " Creating music_reader role..."
Invoke-RestMethod -Uri "http://localhost:9200/_security/role/music_reader" `
  -Method Put `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{
    "indices": [
      {
        "names": [ "musicxml" ],
        "privileges": [ "read", "view_index_metadata" ]
      }
    ]
  }' `
  -Credential (New-Object System.Management.Automation.PSCredential("elastic", (ConvertTo-SecureString $ELASTIC_PASSWORD -AsPlainText -Force)))

# Use a here-string for the JSON payload for clarity:
$bodyKibanabot = @"
{
  "password": "$APP_ES_PASSWORD",
  "roles": [ "kibana_system", "music_reader" ],
  "full_name": "Kibana Bot User"
}
"@

Write-Output "Creating kibanabot user..."
Invoke-RestMethod -Uri "http://localhost:9200/_security/user/kibanabot" `
  -Method Put `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body $bodyKibanabot `
  -Credential (New-Object System.Management.Automation.PSCredential("elastic", (ConvertTo-SecureString $ELASTIC_PASSWORD -AsPlainText -Force)))

Write-Output "Indexing musicxml data..."
Invoke-RestMethod -Uri "http://localhost:9200/musicxml/_bulk" `
  -Method Post `
  -Headers @{ "Content-Type" = "application/json" } `
  -InFile "data/bulk_music.json"

Write-Output "Setup complete"
