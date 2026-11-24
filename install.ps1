<#
Procedural Prompting -- the installer for Windows (Windows PowerShell 5.1 or later).

  pp-install.cmd [-House <folder>] [-Harness claude|codex|gemini|cursor] [-Packages "<names>"] [-NoLaunch]
  powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/VogtVan/pp/main/install.ps1 | iex"

In order: uv, installed when it is missing; the product -- the folder this script stands
in, or, when it is piped, the archive of `main` extracted as `.\pp`; the house, installed
beside the product, or brought up to date when it stands (`pp upgrade --from`, nothing
else); the post's launcher `pp-ui.cmd` (`pp-ui-<name>.cmd` for a house not named house) beside it; the post, opened. Played again, it
changes nothing a house holds but what `pp upgrade` moves.

  PP_UV_INSTALLER   uv's installer, a URL or a file   (https://astral.sh/uv/install.ps1)
  PP_ARCHIVE        the product's archive, a URL or a file   (the archive of `main`)
#>
param(
    [string]$House = "",
    [ValidateSet("claude", "codex", "gemini", "cursor")][string]$Harness = "claude",
    [string]$Packages = "agent team ui",
    [switch]$NoLaunch,
    [switch]$Help
)
$ErrorActionPreference = "Stop"
$Usage = 'usage: pp-install.cmd [-House <folder>] [-Harness claude|codex|gemini|cursor] [-Packages "<names>"] [-NoLaunch]'
$UvInstaller = if ($env:PP_UV_INSTALLER) { $env:PP_UV_INSTALLER } else { "https://astral.sh/uv/install.ps1" }
$Archive = if ($env:PP_ARCHIVE) { $env:PP_ARCHIVE } else { "https://github.com/VogtVan/pp/archive/refs/heads/main.zip" }
$Chosen = $PSBoundParameters.ContainsKey("Harness") -or $PSBoundParameters.ContainsKey("Packages")

function Say([string]$Text) { Write-Host "pp-install: $Text" }
function Fail([string]$Text) { throw "pp-install: $Text" }
function Fetch([string]$From, [string]$To) {
    if ($From -match '^https?://') {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -UseBasicParsing -Uri $From -OutFile $To
    } else {
        Copy-Item -LiteralPath $From -Destination $To
    }
}
function Played([string]$What) { if ($LASTEXITCODE -ne 0) { Fail "$What ended with code $LASTEXITCODE" } }

if ($Help) { Write-Host $Usage; return }

# 1. uv -- installed when missing, then found in this process's PATH
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Say "uv is missing: installing it"
    $got = Join-Path ([IO.Path]::GetTempPath()) ("uv-install-" + [guid]::NewGuid() + ".ps1")
    Fetch $UvInstaller $got
    & powershell -NoProfile -ExecutionPolicy Bypass -File $got
    Played "uv's installer"
    Remove-Item -LiteralPath $got -Force
    $env:Path = (Join-Path $env:USERPROFILE ".local\bin") + ";" + $env:Path
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { Fail "uv was installed but $env:USERPROFILE\.local\bin does not hold it" }
    Say "uv installed -- a new window finds it by itself"
}

# 2. the product -- this script's folder, or the archive extracted as .\pp
if ($PSScriptRoot -and (Test-Path -LiteralPath (Join-Path $PSScriptRoot "engine\pp.py"))) {
    $Source = (Resolve-Path -LiteralPath $PSScriptRoot).Path
    $Archived = $false
} else {
    $Source = Join-Path (Get-Location).Path "pp"
    $Archived = $true
}
if (-not $House) { $House = Join-Path (Split-Path -Parent $Source) "house" }
if (-not [IO.Path]::IsPathRooted($House)) { $House = Join-Path (Get-Location).Path $House }
$House = [IO.Path]::GetFullPath($House)
if ($Archived) {
    if (($House + "\").StartsWith($Source + "\", [StringComparison]::OrdinalIgnoreCase)) {
        Fail "the house $House stands inside $Source, which the archive replaces"
    }
    if (Test-Path -LiteralPath (Join-Path $Source ".git")) {
        Say "$Source is a git clone: left as it is ('git pull' brings it up to date)"
    } else {
        $work = Join-Path ([IO.Path]::GetTempPath()) ("pp-install-" + [guid]::NewGuid())
        New-Item -ItemType Directory -Path $work | Out-Null
        Fetch $Archive (Join-Path $work "pp.zip")
        Expand-Archive -LiteralPath (Join-Path $work "pp.zip") -DestinationPath (Join-Path $work "out")
        $top = @(Get-ChildItem -LiteralPath (Join-Path $work "out") -Directory)[0]
        if (-not ($top -and (Test-Path -LiteralPath (Join-Path $top.FullName "engine\pp.py")))) { Fail "the archive $Archive holds no product" }
        if (Test-Path -LiteralPath $Source) { Remove-Item -LiteralPath $Source -Recurse -Force }
        Move-Item -LiteralPath $top.FullName -Destination $Source
        Remove-Item -LiteralPath $work -Recurse -Force
        Say "the product extracted in $Source"
    }
}

# 3. the house -- installed when absent, brought up to date when it stands
$Console = Join-Path $House "pp.cmd"
if (Test-Path -LiteralPath (Join-Path $House ".pp")) {
    Say "the house $House stands: bringing it up to date"
    if ($Chosen) { Say "a standing house keeps its packages and its harness ('pp add <package>' adds one)" }
    & $Console upgrade --from $Source
    Played "pp upgrade"
} else {
    Say "installing the house $House"
    $names = @($Packages -split '\s+' | Where-Object { $_ })
    & uv run (Join-Path $Source "engine\pp.py") -install $House @names "-$Harness"
    Played "the install"
    # 4. the harness -- its command told when missing, never installed
    $declared = Select-String -LiteralPath (Join-Path $Source "adapters\$Harness\wire.py") -Pattern '^BINARY = "([^"]*)"'
    $binary = if ($declared) { $declared.Matches[0].Groups[1].Value } else { "" }
    if ($binary -and -not (Get-Command $binary -ErrorAction SilentlyContinue)) {
        Say "'$binary' is not on the PATH: install $Harness's command line before the first exchange"
    }
}

# 5. the post's launcher, beside the house, when the house carries the post
$place = Split-Path -Parent $House
$name = Split-Path -Leaf $House
$launcher = if ($name -eq "house") { "pp-ui" } else { "pp-ui-$name" }    # each house of a folder its own launcher
$versions = (& $Console version -json) -join "`n" | ConvertFrom-Json
Played "pp version"
if ($versions.packages.PSObject.Properties.Name -contains "ui") {
    $cmd = "@echo off`r`nrem Opens the post of the house $name beside this file -- written by pp's installer at each of its plays.`r`ncall `"%~dp0$name\pp.cmd`" ui %*`r`n"
    [IO.File]::WriteAllText((Join-Path $place "$launcher.cmd"), $cmd)
    $sh = "#!/bin/sh`n# Opens the post of the house '$name' beside this file -- written by pp's installer at each of its plays.`nexec `"`$(cd -- `"`$(dirname -- `"`$0`")`" && pwd)/$name/pp`" ui `"`$@`"`n"
    [IO.File]::WriteAllText((Join-Path $place $launcher), $sh)
    Say "the post opens with $(Join-Path $place "$launcher.cmd")"
    # 6. the post, on this window
    if (-not $NoLaunch) { & $Console ui }
} else {
    Say "the house carries no post: 'pp add ui' brings it"
}
