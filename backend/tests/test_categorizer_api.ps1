$body = @{
    content = "This is a note about finance and investments."
    meta = @{ filename = "finance_note.txt" }
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/categorize" -ContentType "application/json" -Body $body
