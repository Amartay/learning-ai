# Usage: .\load-dotenv.ps1; python your_script.py

# Path to your .env file
$envFile = ".env"

# Read each line and set environment variables
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$") {
        $name = $matches[1]
        $value = $matches[2].Trim('"')
        [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        $env:$name = $value
    }
}

Write-Host "Environment variables loaded from $envFile."