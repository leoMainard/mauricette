<#
    Arrête les services Mauricette lancés par demarrer.ps1 (MinIO, backend,
    frontend), en repérant les processus qui écoutent sur leurs ports respectifs.
    PostgreSQL n'est pas arrêté : c'est un service Windows partagé avec d'autres projets.
#>

function Arreter-Port {
    param([int[]]$Ports, [string]$Nom)

    $connexions = Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue
    if (-not $connexions) {
        Write-Host "$Nom : rien à arrêter (port(s) $($Ports -join ', ') libre(s))."
        return
    }

    $idsProcessus = $connexions.OwningProcess | Select-Object -Unique
    foreach ($idProcessus in $idsProcessus) {
        Write-Host "$Nom : arrêt du processus $idProcessus..."
        Stop-Process -Id $idProcessus -Force -ErrorAction SilentlyContinue
    }
}

function Arreter-Processus-Par-Motif {
    # Le worker RAG n'écoute sur aucun port : on le repère par sa ligne de commande.
    param([string]$Motif, [string]$Nom)

    $procs = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
        Where-Object { $_.CommandLine -match $Motif }
    if (-not $procs) {
        Write-Host "$Nom : rien à arrêter."
        return
    }

    foreach ($proc in $procs) {
        Write-Host "$Nom : arrêt du processus $($proc.ProcessId)..."
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "=== Mauricette : arrêt des services ===" -ForegroundColor Cyan
Write-Host ""

# Vite incrémente le port si 5173 est occupé : on couvre une petite plage par sécurité.
Arreter-Port -Ports 5173,5174,5175,5176 -Nom "Frontend"
Arreter-Port -Ports 8000 -Nom "Backend"
Arreter-Port -Ports 9000 -Nom "MinIO"
Arreter-Processus-Par-Motif -Motif "worker_rag" -Nom "Worker RAG"

Write-Host ""
Write-Host "PostgreSQL n'est pas arrêté (service Windows partagé)." -ForegroundColor Yellow
