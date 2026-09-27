$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $root ".env"
$venvPath = Join-Path $root ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pythonwExe = Join-Path $venvPath "Scripts\pythonw.exe"

function Find-PythonLauncher {
    foreach ($candidate in @("py", "python")) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            return $candidate
        }
    }

    throw "Python introuvable. Installe Python 3.10+ et relance ce script."
}

function Select-File($title, $filter) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Title = $title
    $dialog.Filter = $filter

    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        return $dialog.FileName
    }

    return $null
}

function Select-Folder($title) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = $title

    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        return $dialog.SelectedPath
    }

    return $null
}

function Invoke-FirstTimeSetup {
    Write-Host ""
    Write-Host "=== Premiere installation de MailForge ===" -ForegroundColor Cyan
    Write-Host ""

    if (-not (Test-Path $venvPath)) {
        Write-Host "Creation de l'environnement virtuel (.venv)..."
        $launcher = Find-PythonLauncher
        & $launcher -m venv $venvPath
    }

    Write-Host "Installation des dependances..."
    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install -r (Join-Path $root "requirements.txt")

    Write-Host ""
    Write-Host "Fournisseur d'envoi des mails :"
    Write-Host "  [1] Resend"
    Write-Host "  [2] Gmail"

    do {
        $choice = Read-Host "Choix (1 ou 2)"
    } while ($choice -ne "1" -and $choice -ne "2")

    $mailDomaine = Read-Host "Domaine utilise pour l'adresse expediteur (ex: exemple.fr)"

    $resendKey = ""
    $credentialsFile = "credentials.json"

    if ($choice -eq "1") {
        $provider = "resend"
        $resendKey = Read-Host "Cle API Resend"
    }
    else {
        $provider = "gmail"

        Write-Host ""
        Write-Host "Selectionne le fichier credentials.json (OAuth Google Cloud)..."
        $picked = Select-File "Selectionne credentials.json" "Fichiers JSON (*.json)|*.json"

        if ($picked) {
            $credentialsFile = $picked
        }
        else {
            $credentialsFile = Read-Host "Chemin vers credentials.json (laisser vide pour 'credentials.json')"
            if ([string]::IsNullOrWhiteSpace($credentialsFile)) {
                $credentialsFile = "credentials.json"
            }
        }
    }

    Write-Host ""
    $useCustomDir = Read-Host "Utiliser un dossier personnalise pour les templates (ex: C:\MesTemplates) ? (o/N)"

    $templatesDir = "templates"

    if ($useCustomDir -match "^[oOyY]") {
        $picked = Select-Folder "Choisis le dossier des templates"

        if ($picked) {
            $templatesDir = $picked
        }
        else {
            $templatesDir = Read-Host "Chemin du dossier templates"
        }

        New-Item -ItemType Directory -Force -Path $templatesDir | Out-Null
    }

    $envLines = @(
        "MAIL_PROVIDER=$provider",
        "RESEND_API_KEY=$resendKey",
        "MAIL_DOMAINE=$mailDomaine",
        "GMAIL_CREDENTIALS_FILE=$credentialsFile",
        "GMAIL_TOKEN_FILE=token.json",
        "LOG_MAX_SIZE_MB=20",
        "LOG_BACKUP_COUNT=32",
        "TEMPLATES_DIR=$templatesDir"
    )

    Set-Content -Path $envPath -Value $envLines -Encoding UTF8

    Write-Host ""
    Write-Host "Configuration enregistree dans .env" -ForegroundColor Green
    Write-Host ""
}

$setupComplete = (Test-Path $envPath) -and (Test-Path $pythonExe)

if (-not $setupComplete) {
    Invoke-FirstTimeSetup
}

Write-Host "Lancement de l'interface graphique..."

$launcherExe = if (Test-Path $pythonwExe) { $pythonwExe } else { $pythonExe }

Start-Process -FilePath $launcherExe -ArgumentList (Join-Path $root "gui.py") -WorkingDirectory $root
