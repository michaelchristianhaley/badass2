param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$BadassArgs
)

$script = Join-Path $PSScriptRoot "badass.py"

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $script @BadassArgs
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $script @BadassArgs
} else {
    throw "Python 3 is required."
}

exit $LASTEXITCODE
