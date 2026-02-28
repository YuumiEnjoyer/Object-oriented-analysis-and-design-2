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

mvn exec:java
