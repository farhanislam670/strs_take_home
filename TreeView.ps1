param(
    [Parameter(Mandatory = $true)]
    [string]$Path,

    [string]$OutputFile = ""
)

if (-Not (Test-Path $Path)) {
    Write-Error "The path '$Path' does not exist."
    exit
}

# We'll store output lines here (for writing to file later)
$global:TreeLines = @()

function Show-Tree {
    param(
        [string]$Folder,
        [string]$Indent = ""
    )

    # Exclude unwanted directories
    $items = Get-ChildItem -Path $Folder | Where-Object {
        $_.Name -notin @('venv', '__pycache__')
    }

    $count = $items.Count
    $i = 0

    foreach ($item in $items) {
        $i++
        $isLast = ($i -eq $count)

        $symbol = if ($isLast) { "\--" } else { "|--" }
        $line = "$Indent$symbol $($item.Name)"
        Write-Host $line
        $global:TreeLines += $line

        if ($item.PSIsContainer) {
            $newIndent = if ($isLast) { "$Indent   " } else { "$Indent|   " }
            Show-Tree -Folder $item.FullName -Indent $newIndent
        }
    }
}

Write-Host $Path
$global:TreeLines += $Path
Show-Tree -Folder $Path

# If an output file path was provided, write to it
if ($OutputFile -ne "") {
    Set-Content -Path $OutputFile -Value $global:TreeLines
    Write-Host "`nFolder structure saved to: $OutputFile"
}
