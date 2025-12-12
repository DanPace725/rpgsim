# Script to clean up file names by removing ID numbers from the end of .md files
# The IDs appear to be 32-character hexadecimal strings

param(
    [string]$Path = ".",
    [switch]$WhatIf
)

function Remove-IdFromFilename {
    param([string]$filename)

    # Pattern: 32-character hex string (0-9, a-f) followed by .md
    # The hex string typically starts with "2" based on the examples
    $pattern = " ([0-9a-f]{32})\.md$"

    if ($filename -match $pattern) {
        $newName = $filename -replace $pattern, ".md"
        return $newName
    }

    return $filename
}

# Get all .md files recursively
$mdFiles = Get-ChildItem -Path $Path -Filter "*.md" -Recurse

foreach ($file in $mdFiles) {
    $newName = Remove-IdFromFilename -filename $file.Name

    if ($newName -ne $file.Name) {
        $newPath = Join-Path -Path $file.DirectoryName -ChildPath $newName

        if ($WhatIf) {
            Write-Host "Would rename: $($file.FullName) -> $newPath"
        } else {
            try {
                Rename-Item -Path $file.FullName -NewName $newName -Force
                Write-Host "Renamed: $($file.Name) -> $newName"
            } catch {
                Write-Warning "Failed to rename $($file.FullName): $($_.Exception.Message)"
            }
        }
    }
}

Write-Host "Cleanup complete. Processed $($mdFiles.Count) .md files."
