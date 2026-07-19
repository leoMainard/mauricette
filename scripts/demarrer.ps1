<#
    Démarre tous les services nécessaires au fonctionnement de Mauricette en local :
    PostgreSQL (service Windows), MinIO (stockage documents), le backend FastAPI
    et le frontend Vite. Chaque service tourne dans sa propre fenêtre PowerShell,
    et le script ne relance rien qui tourne déjà (vérification par port).

    Utilisation : clique-droit > Exécuter avec PowerShell, ou double-clique sur
    demarrer.bat si l'exécution de scripts est bloquée par la politique Windows.
#>

$ErrorActionPreference = "Stop"

# Racine du dépôt = dossier parent de scripts/
$Racine = Split-Path -Parent $PSScriptRoot

function Lire-Env {
    param([string]$Chemin)
    $table = @{}
    if (Test-Path $Chemin) {
        foreach ($ligne in Get-Content $Chemin) {
            if ($ligne -match '^\s*#' -or $ligne -match '^\s*$') { continue }
            if ($ligne -match '^\s*([A-Za-z0-9_]+)\s*=\s*(.*)$') {
                $valeur = $matches[2].Trim().Trim('"').Trim("'")
                $table[$matches[1]] = $valeur
            }
        }
    }
    return $table
}

function Port-Ouvert {
    # Test-NetConnection gère correctement IPv4 et IPv6 (Vite/Node n'écoutent
    # parfois que sur l'un des deux) et évite les pièges du TcpClient "maison".
    param([int]$Port)
    $resultat = Test-NetConnection -ComputerName "localhost" -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
    return [bool]$resultat
}

function Attendre-Port {
    param([int]$Port, [string]$Nom, [int]$TimeoutSecondes = 30)
    Write-Host "  Attente du démarrage de $Nom..." -NoNewline
    $debut = Get-Date
    while (-not (Port-Ouvert $Port)) {
        if (((Get-Date) - $debut).TotalSeconds -gt $TimeoutSecondes) {
            Write-Host " toujours indisponible après $TimeoutSecondes s." -ForegroundColor Yellow
            return $false
        }
        Start-Sleep -Milliseconds 500
        Write-Host "." -NoNewline
    }
    Write-Host " prêt." -ForegroundColor Green
    return $true
}

$variablesEnv = Lire-Env (Join-Path $Racine ".env")

Write-Host "=== Mauricette : démarrage des services ===" -ForegroundColor Cyan
Write-Host ""

# --- 1. PostgreSQL (service Windows) ---
Write-Host "[1/4] PostgreSQL"
$service = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $service) {
    Write-Warning "  Aucun service PostgreSQL trouvé sur cette machine. Vérifie qu'il est installé."
} elseif ($service.Status -eq "Running") {
    Write-Host "  Déjà en cours d'exécution ($($service.Name))." -ForegroundColor Green
} else {
    Write-Host "  Démarrage de $($service.Name)..."
    try {
        Start-Service $service.Name
        Write-Host "  Démarré." -ForegroundColor Green
    } catch {
        Write-Warning "  Échec du démarrage automatique (droits administrateur nécessaires ?). Démarre-le manuellement depuis les Services Windows."
    }
}
Write-Host ""

# --- 2. MinIO (stockage documents, compatible S3) ---
Write-Host "[2/4] MinIO"
if (Port-Ouvert 9000) {
    Write-Host "  Déjà en cours d'exécution (port 9000)." -ForegroundColor Green
} else {
    $minioExe = Join-Path $env:USERPROFILE "Documents\minio.exe"
    if (-not (Test-Path $minioExe)) {
        Write-Host "  minio.exe introuvable, téléchargement depuis dl.min.io..."
        Invoke-WebRequest -Uri "https://dl.min.io/server/minio/release/windows-amd64/minio.exe" -OutFile $minioExe
    }

    $minioUser = if ($variablesEnv["S3_ACCESS_KEY"]) { $variablesEnv["S3_ACCESS_KEY"] } else { "mauricette_admin" }
    $minioPass = if ($variablesEnv["S3_SECRET_KEY"]) { $variablesEnv["S3_SECRET_KEY"] } else { "mauricette_dev_secret_2026" }
    $minioData = Join-Path $Racine "minio_data"
    New-Item -ItemType Directory -Force -Path $minioData | Out-Null

    Write-Host "  Démarrage de MinIO (nouvelle fenêtre)..."
    $commande = "`$env:MINIO_ROOT_USER='$minioUser'; `$env:MINIO_ROOT_PASSWORD='$minioPass'; & '$minioExe' server '$minioData' --console-address ':9001'"
    Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $commande
    Attendre-Port -Port 9000 -Nom "MinIO" | Out-Null
}
Write-Host ""

# --- 3. Backend FastAPI ---
Write-Host "[3/4] Backend (FastAPI)"
if (Port-Ouvert 8000) {
    Write-Host "  Déjà en cours d'exécution (port 8000)." -ForegroundColor Green
} else {
    Write-Host "  Démarrage du backend (nouvelle fenêtre)..."
    $backendDir = Join-Path $Racine "backend"
    $commande = "Set-Location '$backendDir'; uv run uvicorn mauricette.api.main:app --app-dir src --host 127.0.0.1 --port 8000 --reload"
    Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $commande
    Attendre-Port -Port 8000 -Nom "le backend" | Out-Null
}
Write-Host ""

# --- 4. Frontend Vite ---
Write-Host "[4/4] Frontend (Vite)"
if (Port-Ouvert 5173) {
    Write-Host "  Déjà en cours d'exécution (port 5173)." -ForegroundColor Green
} else {
    Write-Host "  Démarrage du frontend (nouvelle fenêtre)..."
    $frontendDir = Join-Path $Racine "frontend"
    $commande = "Set-Location '$frontendDir'; npm run dev"
    Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $commande
    Attendre-Port -Port 5173 -Nom "le frontend" -TimeoutSecondes 60 | Out-Null
}
Write-Host ""

Write-Host "=== Tout est lancé ===" -ForegroundColor Cyan
Write-Host "  MinIO (API)      : http://localhost:9000"
Write-Host "  MinIO (console)  : http://localhost:9001"
Write-Host "  Backend (docs)   : http://localhost:8000/docs"
Write-Host "  Application      : http://localhost:5173"
Write-Host ""
Write-Host "Pour tout arrêter : scripts\arreter.ps1"
