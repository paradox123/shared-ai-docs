$ErrorActionPreference = 'Stop'

$installer = Join-Path $PSScriptRoot '..\tools\sync-windows-skill-links.ps1'
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('shared-skill-sync-' + [guid]::NewGuid().ToString('N'))
$skills = Join-Path $fixture 'skills-repo\skills'
$vendor = Join-Path $fixture 'skills-repo\vendor'
$userHome = Join-Path $fixture 'home'

function Assert($condition, [string] $message) {
    if (-not $condition) { throw $message }
}

function Remove-FixtureJunctions([string] $profilePath) {
    $copilot = Join-Path $profilePath '.copilot\skills'
    $codex = Join-Path $profilePath '.codex\skills'
    $paths = @(
        (Join-Path $profilePath '.agents\skills'),
        (Join-Path $profilePath '.claude\skills'),
        (Join-Path $copilot 'council\agents'),
        (Join-Path $copilot 'council\configs'),
        (Join-Path $copilot 'council\scripts')
    )
    foreach ($parent in @($copilot, $codex)) {
        if (Test-Path -LiteralPath $parent -PathType Container) {
            $paths += @(Get-ChildItem -LiteralPath $parent -Force |
                Where-Object { $_.LinkType -eq 'Junction' } |
                ForEach-Object { $_.FullName })
        }
    }
    foreach ($path in $paths) {
        $item = Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
        if ($item -and $item.LinkType -eq 'Junction') {
            [IO.Directory]::Delete($path)
        }
    }
}

try {
    $own = Join-Path $skills 'own'
    $vendorSkill = Join-Path $vendor 'mattpocock\.agents\skills\vendor'
    $council = Join-Path $skills 'council'
    $councilVendor = Join-Path $vendor 'custom\council-of-high-intelligence'
    foreach ($path in @($own, $vendorSkill, $council, $councilVendor, $userHome)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
    foreach ($name in @('agents', 'configs', 'scripts')) {
        New-Item -ItemType Directory -Path (Join-Path $councilVendor $name) | Out-Null
        Set-Content -LiteralPath (Join-Path $council $name) -Value "../../vendor/custom/council-of-high-intelligence/$name"
    }
    Set-Content -LiteralPath (Join-Path $own 'SKILL.md') -Value "---`nname: own`n---"
    Set-Content -LiteralPath (Join-Path $vendorSkill 'SKILL.md') -Value "---`nname: vendor`n---"
    Set-Content -LiteralPath (Join-Path $skills 'vendor') -Value '../vendor/mattpocock/.agents/skills/vendor'
    Set-Content -LiteralPath (Join-Path $councilVendor 'SKILL.codex.md') -Value "---`nname: council`n---"
    Set-Content -LiteralPath (Join-Path $council 'SKILL.md') -Value '../../vendor/custom/council-of-high-intelligence/SKILL.codex.md'
    $system = Join-Path $userHome '.codex\skills\.system'
    New-Item -ItemType Directory -Path $system -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $system 'keep.txt') -Value 'untouched'
    $foreignCopilot = Join-Path $userHome '.copilot\skills\foreign'
    $foreignCodex = Join-Path $userHome '.codex\skills\foreign'
    New-Item -ItemType Directory -Path $foreignCopilot -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $foreignCopilot 'SKILL.md') -Value 'user-owned'
    New-Item -ItemType Junction -Path $foreignCodex -Target $foreignCopilot | Out-Null

    & $installer -SourceSkillsPath $skills -UserHome $userHome | Out-Null
    $copilot = Join-Path $userHome '.copilot\skills'
    foreach ($name in @('own', 'vendor', 'council')) {
        Assert (Test-Path -LiteralPath (Join-Path $copilot "$name\SKILL.md") -PathType Leaf) "Copilot cannot load $name"
        Assert (Test-Path -LiteralPath (Join-Path $userHome ".codex\skills\$name\SKILL.md") -PathType Leaf) "Codex cannot load $name"
        Assert (Test-Path -LiteralPath (Join-Path $userHome ".agents\skills\$name\SKILL.md") -PathType Leaf) "Agents cannot load $name"
        Assert (Test-Path -LiteralPath (Join-Path $userHome ".claude\skills\$name\SKILL.md") -PathType Leaf) "Claude cannot load $name"
    }
    Assert ((Get-Item -LiteralPath (Join-Path $copilot 'vendor')).LinkType -eq 'Junction') 'Vendor must be linked to its source'
    Assert ((Get-Item -LiteralPath (Join-Path $copilot 'council\agents')).LinkType -eq 'Junction') 'Council assets must be linked'
    Assert ((Get-Content -LiteralPath (Join-Path $copilot 'council\SKILL.md') -Raw) -match 'name: council') 'Council manifest was not materialized'
    Assert (Test-Path -LiteralPath (Join-Path $system 'keep.txt')) 'Existing Codex system skill was removed'
    Assert (Test-Path -LiteralPath (Join-Path $foreignCodex 'SKILL.md') -PathType Leaf) 'Foreign Codex junction into Copilot was removed'
    Assert ((Get-Content -LiteralPath (Join-Path $foreignCopilot 'SKILL.md') -Raw).Trim() -eq 'user-owned') 'Foreign Copilot skill was changed'

    Set-Content -LiteralPath (Join-Path $foreignCopilot '.shared-ai-docs-source') -Value $own
    & $installer -SourceSkillsPath $skills -UserHome $userHome | Out-Null
    Assert (Test-Path -LiteralPath (Join-Path $foreignCodex 'SKILL.md') -PathType Leaf) 'Marker for another canonical skill claimed a foreign Copilot directory'
    Assert ((Get-Content -LiteralPath (Join-Path $foreignCopilot 'SKILL.md') -Raw).Trim() -eq 'user-owned') 'Mismatched marker allowed foreign manifest deletion'

    Set-Content -LiteralPath (Join-Path $councilVendor 'SKILL.codex.md') -Value "---`nname: updated-council`n---"
    & $installer -SourceSkillsPath $skills -UserHome $userHome | Out-Null
    Assert ((Get-Content -LiteralPath (Join-Path $copilot 'council\SKILL.md') -Raw) -match 'name: updated-council') 'Council manifest did not refresh'
    Remove-Item -LiteralPath (Join-Path $skills 'vendor') -Force
    & $installer -SourceSkillsPath $skills -UserHome $userHome | Out-Null
    Assert (-not (Test-Path -LiteralPath (Join-Path $copilot 'vendor'))) 'Removed vendor skill remains in Copilot'
    Assert (-not (Test-Path -LiteralPath (Join-Path $userHome '.codex\skills\vendor'))) 'Removed vendor skill remains in Codex'
    Assert (Test-Path -LiteralPath (Join-Path $system 'keep.txt')) 'Unmanaged skill was removed'

    $external = Join-Path $fixture 'external-skill'
    New-Item -ItemType Directory -Path $external | Out-Null
    New-Item -ItemType Junction -Path (Join-Path $userHome '.codex\skills\external') -Target $external | Out-Null
    Remove-Item -LiteralPath $council -Recurse -Force
    $userNote = Join-Path $copilot 'council\user-note.txt'
    Set-Content -LiteralPath $userNote -Value 'keep'
    $failed = $false
    try { & $installer -SourceSkillsPath $skills -UserHome $userHome | Out-Null } catch { $failed = $true }
    Assert $failed 'Installer removed a wrapper with user-owned files'
    Assert (Test-Path -LiteralPath (Join-Path $copilot 'council\SKILL.md')) 'Installer partially removed council assets'
    Assert (Test-Path -LiteralPath $userNote) 'User-owned wrapper file was removed'
    Remove-Item -LiteralPath $userNote -Force
    & $installer -SourceSkillsPath $skills -UserHome $userHome | Out-Null
    Assert (-not (Test-Path -LiteralPath (Join-Path $copilot 'council'))) 'Removed council wrapper remains in Copilot'
    Assert (-not (Test-Path -LiteralPath (Join-Path $userHome '.codex\skills\council'))) 'Removed council remains in Codex'
    Assert (Test-Path -LiteralPath (Join-Path $userHome '.codex\skills\external')) 'Unmanaged junction was removed'

    $missing = Join-Path $skills 'missing'
    Set-Content -LiteralPath $missing -Value '../vendor/no-such-skill'
    $failed = $false
    try { & $installer -SourceSkillsPath $skills -UserHome $userHome | Out-Null } catch { $failed = $true }
    Assert $failed 'Installer silently accepted a broken vendor link'
    Assert (-not (Test-Path -LiteralPath (Join-Path $copilot 'missing'))) 'Broken vendor link was installed'
    Remove-Item -LiteralPath $missing -Force

    $conflictHome = Join-Path $fixture 'conflict-home'
    $conflict = Join-Path $conflictHome '.copilot\skills\own'
    New-Item -ItemType Directory -Path $conflict -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $conflict 'SKILL.md') -Value 'user-owned'
    $failed = $false
    try { & $installer -SourceSkillsPath $skills -UserHome $conflictHome | Out-Null } catch { $failed = $true }
    Assert $failed 'Installer overwrote a pre-existing skill directory'
    Assert ((Get-Content -LiteralPath (Join-Path $conflict 'SKILL.md') -Raw) -match 'user-owned') 'Pre-existing skill was changed'

    'Windows skill sync: all checks passed'
}
finally {
    Remove-FixtureJunctions $userHome
    Remove-FixtureJunctions (Join-Path $fixture 'conflict-home')
    if (Test-Path -LiteralPath $fixture) {
        Remove-Item -LiteralPath $fixture -Recurse -Force
    }
}
