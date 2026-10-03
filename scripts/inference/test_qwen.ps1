param(
    [string]$Model = 'qwen2.5-7b-instruct:q4_k_m-local'
)

$ErrorActionPreference = 'Stop'
$api = 'http://127.0.0.1:11434'
$prompt = 'Explique en français, en cinq phrases maximum, la différence entre un contrat à durée déterminée et un contrat à durée indéterminée. Si une information te manque, indique-le.'

try {
    $version = Invoke-RestMethod -Uri "$api/api/version" -TimeoutSec 5
    $catalogue = Invoke-RestMethod -Uri "$api/api/tags" -TimeoutSec 5
} catch {
    throw "Connexion à Ollama impossible sur $api. Vérifier que l'application est lancée. Détail : $($_.Exception.Message)"
}

$entree = $catalogue.models | Where-Object { $_.name -eq $Model } | Select-Object -First 1
if ($null -eq $entree) {
    throw "Modèle local absent : $Model. Vérifier son nom avec 'ollama list' et suivre la procédure d'import du rapport."
}
if ($entree.details.quantization_level -ne 'Q4_K_M') {
    throw "Quantification inattendue : $($entree.details.quantization_level). Q4_K_M est requis."
}

try {
    $charges = Invoke-RestMethod -Uri "$api/api/ps" -TimeoutSec 5
    $etaitCharge = [bool]($charges.models | Where-Object { $_.name -eq $Model })

    $requete = @{
        model = $Model
        prompt = $prompt
        stream = $false
        keep_alive = '30m'
        options = @{
            temperature = 0.2
            num_predict = 200
            num_ctx = 4096
        }
    } | ConvertTo-Json -Depth 4

    $resultat = Invoke-RestMethod `
        -Uri "$api/api/generate" `
        -Method Post `
        -ContentType 'application/json; charset=utf-8' `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($requete)) `
        -TimeoutSec 300
} catch {
    throw "Inférence locale impossible pour $Model. Détail : $($_.Exception.Message)"
}

Write-Output "Modèle : $($entree.name)"
Write-Output "Digest local : $($entree.digest)"
Write-Output "Quantification : $($entree.details.quantization_level)"
Write-Output "Version Ollama : $($version.version)"
Write-Output "Déjà chargé avant l'appel : $etaitCharge"
Write-Output "Réponse :"
Write-Output $resultat.response
Write-Output "Fin de génération : $($resultat.done_reason)"
Write-Output ("Temps total : {0:N3} s" -f ($resultat.total_duration / 1e9))
Write-Output ("Temps de chargement : {0:N3} s" -f ($resultat.load_duration / 1e9))
Write-Output ("Temps de génération : {0:N3} s" -f ($resultat.eval_duration / 1e9))
Write-Output "Tokens générés : $($resultat.eval_count)"

if ($resultat.eval_duration -gt 0) {
    Write-Output ("Débit : {0:N2} tokens/s" -f (
        $resultat.eval_count / ($resultat.eval_duration / 1e9)
    ))
}

if (-not $resultat.done -or
    [string]::IsNullOrWhiteSpace($resultat.response) -or
    $resultat.done_reason -ne 'stop') {
    throw "La réponse est absente ou la génération ne s'est pas terminée normalement."
}
