function Load-Env {
    param( [string]$FP )
    Get-Content $FP | foreach {
        $name, $value = $_.split('=')
        if ([string]::IsNullOrWhiteSpace($name) -or $name.Contains('#')) { return }
        Set-Content env:\$name $value
    }
}

if (Test-Path -Path "../.env" -PathType Leaf) {
    Load-Env "../.env"
} elseif (Test-Path -Path "../.env.temp" -PathType Leaf) {
    Load-Env "../.env.temp"
}

if (Test-Path -Path "venv") {
    $pythonPath = Resolve-Path ".\venv\Scripts\python.exe"
} elseif (Test-Path -Path ".venv") {
    $pythonPath = Resolve-Path ".\.venv\Scripts\python.exe"
} else {
    $pythonPath = "python"
}

Invoke-Expression "$pythonPath src/main.py"
