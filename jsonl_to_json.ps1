param(
    [Parameter(Mandatory=$true)]
    [string]$InputFile,

    [Parameter(Mandatory=$false)]
    [string]$OutputFile
)

# If no output file specified, use input filename with .json extension
if (-not $OutputFile) {
    $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, ".json")
}

# Read all lines from JSONL file and parse as JSON objects
$jsonObjects = @()
Get-Content -Path $InputFile | ForEach-Object {
    if ($_.Trim()) {  # Skip empty lines
        try {
            $jsonObjects += ConvertFrom-Json $_
        } catch {
            Write-Warning "Failed to parse line: $($_.Substring(0, [Math]::Min(50, $_.Length)))..."
        }
    }
}

# Convert to JSON array
$jsonArray = ConvertTo-Json -InputObject $jsonObjects -Depth 10

# Write to output file
$jsonArray | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "Converted $InputFile to $OutputFile"
Write-Host "Processed $($jsonObjects.Count) JSON objects"
