[CmdletBinding()]
param(
	[switch]$StartApi,
	[switch]$StartWorker,
	[switch]$Stop,
	[string]$BackendPath = "$PSScriptRoot\..\backend",
	[string]$LogPath = "$PSScriptRoot\..\logs"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ApprovedHosts = @('localhost', '127.0.0.1')
$ApprovedPorts = @(5432)
$ApprovedDatabases = @('orvexa_db')
$RequiredSchemaRevision = '0006_stage2_extraction_jobs'
$WorkerPidFile = Join-Path $LogPath 'worker.pid'
$ApiPidFile = Join-Path $LogPath 'api.pid'

function Get-DatabaseTarget {
	if ($env:DATABASE_URL) {
		$uri = [System.Uri]$env:DATABASE_URL
		if ($uri.Scheme -notin @('postgresql', 'postgresql+asyncpg')) {
			throw 'DATABASE_URL must use PostgreSQL.'
		}
		$hostName = $uri.Host.ToLowerInvariant()
		$port = if ($uri.Port -gt 0) { $uri.Port } else { 5432 }
		$database = $uri.AbsolutePath.TrimStart('/')
	}
	else {
		$hostName = if ($env:POSTGRES_HOST) { $env:POSTGRES_HOST.ToLowerInvariant() } else { 'localhost' }
		$port = if ($env:POSTGRES_PORT) { [int]$env:POSTGRES_PORT } else { 5432 }
		$database = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { 'orvexa_db' }
	}
	return @{ Host = $hostName; Port = $port; Database = $database }
}

function Assert-ApprovedWorkerConfiguration {
	$target = Get-DatabaseTarget
	if ($target.Database -eq 'nova_health') { throw 'Worker refuses the nova_health database.' }
	if ($target.Host -notin $ApprovedHosts) { throw "Worker database host '$($target.Host)' is not explicitly approved." }
	if ($target.Port -notin $ApprovedPorts) { throw "Worker database port '$($target.Port)' is not explicitly approved." }
	if ($target.Database -notin $ApprovedDatabases) { throw "Worker database '$($target.Database)' is not explicitly approved." }
	if ($env:WORKER_SCHEMA_REVISION -ne $RequiredSchemaRevision) {
		throw "Worker requires independently verified schema revision $RequiredSchemaRevision. This launcher never runs migrations."
	}
	Write-Host "Worker configuration approved for $($target.Host):$($target.Port)/$($target.Database); schema prerequisite asserted as $RequiredSchemaRevision."
}

function Write-PidFile([string]$Path, [System.Diagnostics.Process]$Process) {
	Set-Content -Path $Path -Value $Process.Id -NoNewline
}

function Stop-ManagedProcess([string]$Path, [string]$Name) {
	if (-not (Test-Path $Path)) { return }
	$processId = [int](Get-Content $Path)
	$process = Get-Process -Id $processId -ErrorAction SilentlyContinue
	if ($process) {
		Stop-Process -Id $processId -ErrorAction SilentlyContinue
		Write-Host "Stopped $Name process $processId."
	}
	Remove-Item $Path -Force -ErrorAction SilentlyContinue
}

if (-not ($StartApi -or $StartWorker -or $Stop)) {
	throw 'Specify -StartApi, -StartWorker, or -Stop.'
}

New-Item -ItemType Directory -Force -Path $LogPath | Out-Null

if ($Stop) {
	Stop-ManagedProcess $WorkerPidFile 'worker'
	Stop-ManagedProcess $ApiPidFile 'API'
}

if ($StartApi) {
	$apiOut = Join-Path $LogPath 'api.out.log'
	$apiErr = Join-Path $LogPath 'api.err.log'
	$apiHost = if ($env:API_HOST) { $env:API_HOST } else { '127.0.0.1' }
	$apiPort = if ($env:API_PORT) { $env:API_PORT } else { '8000' }
	$api = Start-Process -FilePath 'python' -WorkingDirectory $BackendPath -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', $apiHost, '--port', $apiPort) -RedirectStandardOutput $apiOut -RedirectStandardError $apiErr -PassThru
	Write-PidFile $ApiPidFile $api
	Write-Host "Started API process $($api.Id). Logs: $apiOut and $apiErr"
}

if ($StartWorker) {
	Assert-ApprovedWorkerConfiguration
	$workerOut = Join-Path $LogPath 'worker.out.log'
	$workerErr = Join-Path $LogPath 'worker.err.log'
	$worker = Start-Process -FilePath 'python' -WorkingDirectory $BackendPath -ArgumentList @('-m', 'app.workers.document_worker') -RedirectStandardOutput $workerOut -RedirectStandardError $workerErr -PassThru
	Write-PidFile $WorkerPidFile $worker
	Write-Host "Started worker process $($worker.Id). Logs: $workerOut and $workerErr"
}
