param(
    [string] $SourceSkillsPath = (Join-Path $PSScriptRoot '..\skills'),
    [string] $UserHome = $env:USERPROFILE
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$source = [IO.Path]::GetFullPath($SourceSkillsPath)
$skillsRepo = Split-Path -Parent $source
$copilot = Join-Path $UserHome '.copilot\skills'
$codex = Join-Path $UserHome '.codex\skills'
$managedRoots = @($source, (Join-Path $skillsRepo 'vendor'), (Join-Path $skillsRepo 'active-skills'))
$markerName = '.shared-ai-docs-source'

function Test-UnderRoot([string] $path, [string] $root) {
    $path = [IO.Path]::GetFullPath($path)
    $root = [IO.Path]::GetFullPath($root).TrimEnd('\')
    return $path.Equals($root, [StringComparison]::OrdinalIgnoreCase) -or
        $path.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase)
}

function Test-ManagedTarget([string] $target) {
    if (-not [IO.Path]::IsPathRooted($target)) { return $false }
    foreach ($root in $managedRoots) {
        if (Test-UnderRoot $target $root) { return $true }
    }
    $target = [IO.Path]::GetFullPath($target).TrimEnd('\')
    $copilotRoot = [IO.Path]::GetFullPath($copilot).TrimEnd('\')
    if ((Split-Path -Parent $target) -ne $copilotRoot) { return $false }
    $marker = Join-Path $target $markerName
    if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) { return $false }
    $markedSource = (Get-Content -LiteralPath $marker -Raw).Trim()
    if (-not [IO.Path]::IsPathRooted($markedSource)) { return $false }
    # The source entry may be gone when cleaning up a stale managed shim.
    $expectedSource = Join-Path $source (Split-Path -Leaf $target)
    return [IO.Path]::GetFullPath($markedSource).TrimEnd('\').Equals(
        $expectedSource.TrimEnd('\'), [StringComparison]::OrdinalIgnoreCase)
}

function Resolve-LinkPlaceholder([string] $path) {
    $link = (Get-Content -LiteralPath $path -Raw).Trim()
    if ($link.Length -eq 0 -or $link.Length -gt 300 -or $link -match '[\r\n]' -or
        [IO.Path]::IsPathRooted($link)) {
        throw "Invalid checked-out symlink: $path"
    }
    $target = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $path) $link.Replace('/', '\')))
    if (-not (Test-UnderRoot $target $skillsRepo) -or -not (Test-Path -LiteralPath $target)) {
        throw "Missing or external symlink target for ${path}: $target"
    }
    return $target
}

function Test-Manifest([string] $path) {
    return (Test-Path -LiteralPath $path -PathType Leaf) -and
        (Get-Content -LiteralPath $path -TotalCount 1) -eq '---'
}

function Get-ExistingItem([string] $path) {
    $parent = Split-Path -Parent $path
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { return $null }
    return Get-ChildItem -LiteralPath $parent -Force |
        Where-Object { $_.Name -eq (Split-Path -Leaf $path) } |
        Select-Object -First 1
}

function Ensure-Directory([string] $path) {
    $existing = Get-ExistingItem $path
    if ($existing) {
        if (-not $existing.PSIsContainer -or $existing.LinkType) {
            throw "Refusing to replace an existing skill directory: $path"
        }
        return
    }
    New-Item -ItemType Directory -Path $path -Force | Out-Null
}

function Get-JunctionTarget($item) {
    $target = [string] @($item.Target)[0]
    if (-not [IO.Path]::IsPathRooted($target)) {
        $target = Join-Path (Split-Path -Parent $item.FullName) $target
    }
    return [IO.Path]::GetFullPath($target)
}

function Ensure-Junction([string] $path, [string] $target) {
    $existing = Get-ExistingItem $path
    if ($existing) {
        if ($existing.LinkType -ne 'Junction' -and $existing.LinkType -ne 'SymbolicLink') {
            throw "Refusing to replace an existing skill: $path"
        }
        $oldTarget = Get-JunctionTarget $existing
        if ($oldTarget.Equals($target, [StringComparison]::OrdinalIgnoreCase)) { return }
        if (-not (Test-ManagedTarget $oldTarget)) {
            throw "Refusing to replace an unmanaged skill link: $path"
        }
        [IO.Directory]::Delete($path)
    }
    New-Item -ItemType Junction -Path $path -Target $target | Out-Null
}

function Remove-ManagedShim([string] $path) {
    $marker = Join-Path $path $markerName
    if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) { return $false }
    if (-not (Test-ManagedTarget $path)) { return $false }
    $items = @(Get-ChildItem -LiteralPath $path -Force)
    foreach ($item in $items) {
        if ($item.LinkType -eq 'Junction' -or $item.LinkType -eq 'SymbolicLink') {
            if (-not (Test-ManagedTarget (Get-JunctionTarget $item))) {
                throw "Unmanaged link inside skill directory: $($item.FullName)"
            }
        } elseif ($item.Name -ne 'SKILL.md' -and $item.Name -ne $markerName) {
            throw "Unmanaged file inside skill directory: $($item.FullName)"
        }
    }
    foreach ($item in $items) {
        if ($item.LinkType -eq 'Junction' -or $item.LinkType -eq 'SymbolicLink') {
            [IO.Directory]::Delete($item.FullName)
        } else {
            Remove-Item -LiteralPath $item.FullName -Force
        }
    }
    [IO.Directory]::Delete($path)
    return $true
}

function Ensure-Shim($spec) {
    $path = Join-Path $copilot $spec.Name
    $existing = Get-ExistingItem $path
    if ($existing) {
        if ($existing.LinkType) {
            if (-not (Test-ManagedTarget (Get-JunctionTarget $existing))) {
                throw "Refusing to replace an unmanaged skill link: $path"
            }
            [IO.Directory]::Delete($path)
            $existing = $null
        } elseif (-not $existing.PSIsContainer -or
            -not (Test-Path -LiteralPath (Join-Path $path $markerName) -PathType Leaf) -or
            (Get-Content -LiteralPath (Join-Path $path $markerName) -Raw).Trim() -ne $spec.Source) {
            throw "Refusing to replace an existing skill directory: $path"
        }
    }
    if (-not $existing) {
        New-Item -ItemType Directory -Path $path | Out-Null
        Set-Content -LiteralPath (Join-Path $path $markerName) -Value $spec.Source
    }
    Copy-Item -LiteralPath $spec.Manifest -Destination (Join-Path $path 'SKILL.md') -Force
    foreach ($asset in $spec.Assets) {
        Ensure-Junction (Join-Path $path $asset.Name) $asset.Target
    }
}

function Remove-StaleManagedSkills([string] $path, [string[]] $names) {
    foreach ($item in Get-ChildItem -LiteralPath $path -Force) {
        if ($names -contains $item.Name) { continue }
        if ($item.LinkType -eq 'Junction' -or $item.LinkType -eq 'SymbolicLink') {
            if (Test-ManagedTarget (Get-JunctionTarget $item)) {
                [IO.Directory]::Delete($item.FullName)
            }
        } elseif ($item.PSIsContainer -and $path -eq $copilot) {
            Remove-ManagedShim $item.FullName | Out-Null
        }
    }
}

if (-not (Test-Path -LiteralPath $source -PathType Container)) {
    throw "Missing shared skills directory: $source"
}
if (-not (Test-Path -LiteralPath $UserHome -PathType Container)) {
    throw "Missing user home directory: $UserHome"
}

$specs = @(
    foreach ($entry in Get-ChildItem -LiteralPath $source -Force) {
        if ($entry.PSIsContainer) {
            $manifest = Join-Path $entry.FullName 'SKILL.md'
            if (Test-Manifest $manifest) {
                [pscustomobject]@{ Name = $entry.Name; Mode = 'link'; Target = $entry.FullName }
                continue
            }
            if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
                throw "Missing skill manifest: $manifest"
            }
            $resolvedManifest = Resolve-LinkPlaceholder $manifest
            if (-not (Test-Manifest $resolvedManifest)) {
                throw "Invalid skill manifest: $resolvedManifest"
            }
            $assets = @(
                foreach ($asset in Get-ChildItem -LiteralPath $entry.FullName -Force |
                    Where-Object { $_.Name -ne 'SKILL.md' }) {
                    $target = if ($asset.PSIsContainer) { $asset.FullName } else {
                        Resolve-LinkPlaceholder $asset.FullName
                    }
                    if (-not (Test-Path -LiteralPath $target -PathType Container)) {
                        throw "Unsupported non-directory skill asset: $($asset.FullName)"
                    }
                    [pscustomobject]@{ Name = $asset.Name; Target = $target }
                }
            )
            [pscustomobject]@{
                Name = $entry.Name; Mode = 'shim'; Source = $entry.FullName
                Manifest = $resolvedManifest; Assets = $assets
            }
        } else {
            $target = Resolve-LinkPlaceholder $entry.FullName
            if (-not (Test-Path -LiteralPath $target -PathType Container) -or
                -not (Test-Manifest (Join-Path $target 'SKILL.md'))) {
                throw "Invalid vendor skill: $target"
            }
            [pscustomobject]@{ Name = $entry.Name; Mode = 'link'; Target = $target }
        }
    }
)
if ($specs.Count -eq 0) { throw "No active skills in $source" }

Ensure-Directory $copilot
Ensure-Directory $codex
foreach ($spec in $specs) {
    $runtimePath = Join-Path $copilot $spec.Name
    if ($spec.Mode -eq 'shim') {
        Ensure-Shim $spec
        $codexTarget = $runtimePath
    } else {
        Ensure-Junction $runtimePath $spec.Target
        $codexTarget = $spec.Target
    }
    Ensure-Junction (Join-Path $codex $spec.Name) $codexTarget
}
foreach ($client in @('.agents', '.claude')) {
    $parent = Join-Path $UserHome $client
    Ensure-Directory $parent
    Ensure-Junction (Join-Path $parent 'skills') $copilot
}

$names = @($specs | ForEach-Object { $_.Name })
Remove-StaleManagedSkills $codex $names
Remove-StaleManagedSkills $copilot $names
Write-Output "Synced $($specs.Count) global skills for Copilot, Codex, Agents, and Claude."
