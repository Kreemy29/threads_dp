# PowerShell script to run the Captions Generator API
# This works around the issue with '&&' not working in PowerShell

# Change to the correct directory
Set-Location -Path $PSScriptRoot

Write-Host "Starting server from directory: $PSScriptRoot"
Write-Host "Make sure you're in the captions_generator directory!"

# Run the uvicorn server with the correct module path
# The . before api:app ensures it uses the current directory
python -m uvicorn api:app --reload

# If the above fails, try this alternative command as a fallback
# This explicitly gives uvicorn the path to the current directory
# if ($LASTEXITCODE -ne 0) {
#    Write-Host "First attempt failed, trying alternative method..."
#    python -c "import uvicorn; uvicorn.run('api:app', reload=True)"
# } 