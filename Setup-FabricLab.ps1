<#
.SYNOPSIS
  Builds the Fabric DP-600/DP-700 practice lab: generates sample data locally and
  (optionally) provisions a Fabric workspace + lakehouse and uploads the data to OneLake.

.USAGE
  1) Put this script in the study folder, open PowerShell, then run:
       .\Setup-FabricLab.ps1                       # data + Fabric provisioning
       .\Setup-FabricLab.ps1 -SkipFabric           # only generate data locally
       .\Setup-FabricLab.ps1 -CapacityId <guid>    # force a specific capacity
  2) Requirements: PowerShell 5.1+ ; Azure CLI (auto-install via winget if you agree).
  3) The signed-in account needs permission to create workspaces and a Fabric capacity
     (Trial or F SKU) - the script picks the first active capacity unless -CapacityId is given.

  The script is idempotent: re-running reuses the workspace and lakehouse if they exist.
#>
[CmdletBinding()]
param(
    [string]$Root = $PSScriptRoot,
    [string]$WorkspaceName = "fabric-prep-lab",
    [string]$LakehouseName = "lh_prep",
    [string]$CapacityId = "",
    [int]$Seed = 42,
    [switch]$SkipFabric
)

$ErrorActionPreference = "Stop"
if (-not $Root) { $Root = (Get-Location).Path }
$DataDir = Join-Path $Root "data"
$FabricApi = "https://api.fabric.microsoft.com/v1"
$OneLakeHost = "https://onelake.dfs.fabric.microsoft.com"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

# ---------------------------------------------------------------------------
# 1. Local data generation
# ---------------------------------------------------------------------------
$rnd = New-Object System.Random($Seed)
function Pick($arr) { return $arr[$rnd.Next(0, $arr.Count)] }
function New-Writer($path) {
    $dir = Split-Path $path -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    return New-Object System.IO.StreamWriter($path, $false, (New-Object System.Text.UTF8Encoding($false)))
}
function Esc($s) {
    if ($null -eq $s) { return "" }
    $s = [string]$s
    if ($s.Contains(",") -or $s.Contains('"')) { return '"' + $s.Replace('"', '""') + '"' }
    return $s
}

function New-LabData {
    Write-Step "Generating sample data in $DataDir"
    $first = @("Ali","Sara","Reza","Neda","Omid","Maryam","Hamid","Leila","Kian","Parisa","John","Emma","Liam","Olivia","Noah","Mia")
    $last  = @("Ahmadi","Karimi","Hosseini","Rahimi","Smith","Brown","Lee","Garcia","Khan","Mohammadi","Taylor","Wilson")
    $cities = @("Toronto","Vancouver","Montreal","Calgary","Ottawa","Seattle","Boston","Austin","Berlin","London")
    $countries = @{ Toronto="Canada"; Vancouver="Canada"; Montreal="Canada"; Calgary="Canada"; Ottawa="Canada"; Seattle="USA"; Boston="USA"; Austin="USA"; Berlin="Germany"; London="UK" }
    $segments = @("Consumer","SMB","Enterprise")

    # ---- customers day1 ----
    $cust = @()
    $w = New-Writer (Join-Path $DataDir "customers\customers_day1.csv")
    $w.WriteLine("customer_id,first_name,last_name,email,city,country,segment,signup_date,updated_at")
    for ($i = 1; $i -le 1000; $i++) {
        $id = "C{0:D5}" -f $i
        $fn = Pick $first; $ln = Pick $last; $city = Pick $cities; $seg = Pick $segments
        $su = (Get-Date "2024-01-01").AddDays($rnd.Next(0, 700)).ToString("yyyy-MM-dd")
        $row = [pscustomobject]@{ id=$id; fn=$fn; ln=$ln; city=$city; seg=$seg; su=$su }
        $cust += $row
        $w.WriteLine(("{0},{1},{2},{3}.{4}{5}@example.com,{6},{7},{8},{9},{10}" -f $id,$fn,$ln,$fn.ToLower(),$ln.ToLower(),$i,$city,$countries[$city],$seg,$su,"2026-01-01T00:00:00"))
    }
    $w.Close()

    # ---- customers day2 (changes + new, some dirty country) ----
    $w = New-Writer (Join-Path $DataDir "customers\customers_day2.csv")
    $w.WriteLine("customer_id,first_name,last_name,email,city,country,segment,signup_date,updated_at")
    $changed = $cust | Get-Random -Count 100 -SetSeed $Seed
    foreach ($c in $changed) {
        $city = Pick $cities; $seg = Pick $segments
        $country = $countries[$city]
        if ($rnd.Next(0,10) -eq 0) { $country = $country + " " }
        $w.WriteLine(("{0},{1},{2},{3}.{4}@example.com,{5},{6},{7},{8},{9}" -f $c.id,$c.fn,$c.ln,$c.fn.ToLower(),$c.ln.ToLower(),$city,$country,$seg,$c.su,"2026-02-01T00:00:00"))
    }
    for ($i = 1001; $i -le 1050; $i++) {
        $id = "C{0:D5}" -f $i
        $fn = Pick $first; $ln = Pick $last; $city = Pick $cities; $seg = Pick $segments
        $w.WriteLine(("{0},{1},{2},{3}.{4}{5}@example.com,{6},{7},{8},{9},{10}" -f $id,$fn,$ln,$fn.ToLower(),$ln.ToLower(),$i,$city,$countries[$city],$seg,"2026-02-01","2026-02-01T00:00:00"))
    }
    $w.Close()

    # ---- products ----
    $cats = @("Electronics","Home","Sports","Books","Toys","Clothing")
    $w = New-Writer (Join-Path $DataDir "products\products.csv")
    $w.WriteLine("product_id,product_name,category,unit_cost,list_price")
    for ($i = 1; $i -le 200; $i++) {
        $cost = [math]::Round(5 + $rnd.NextDouble() * 200, 2)
        $price = [math]::Round($cost * (1.2 + $rnd.NextDouble()), 2)
        $name = "Product " + $i
        if ($i % 40 -eq 0) { $name = "  " + $name + "  " }   # dirty: extra spaces
        $w.WriteLine(("P{0:D4},{1},{2},{3},{4}" -f $i,$name,(Pick $cats),$cost,$price))
    }
    # dirty: duplicate product row
    $w.WriteLine(("P{0:D4},{1},{2},{3},{4}" -f 5,"Product 5","Home",10.5,19.99))
    $w.Close()

    # ---- stores ----
    $regions = @("East","West","Central","North")
    $w = New-Writer (Join-Path $DataDir "stores\stores.csv")
    $w.WriteLine("store_id,store_name,region,city,open_date")
    for ($i = 1; $i -le 20; $i++) {
        $w.WriteLine(("S{0:D2},Store {0},{1},{2},{3}" -f $i,(Pick $regions),(Pick $cities),(Get-Date "2018-01-01").AddDays($rnd.Next(0,2000)).ToString("yyyy-MM-dd")))
    }
    $w.Close()

    # ---- orders (3 batches) ----
    $statuses = @("shipped","SHIPPED","Shipped ","delivered","pending","cancelled","returned")
    $channels = @("web","store","mobile")
    $orderIdx = 0
    $batch1Lines = New-Object System.Collections.Generic.List[string]
    for ($b = 1; $b -le 3; $b++) {
        $start = @("2026-01-01","2026-03-01","2026-05-01")[$b-1]
        $count = @(5000,5000,4000)[$b-1]
        $lines = New-Object System.Collections.Generic.List[string]
        for ($i = 1; $i -le $count; $i++) {
            $orderIdx++
            $oid = "O{0:D6}" -f $orderIdx
            $ts = (Get-Date $start).AddMinutes($rnd.Next(0, 60*24*58))
            $tsText = $ts.ToString("yyyy-MM-ddTHH:mm:ss")
            if ($rnd.Next(0,100) -lt 1) { $tsText = $ts.ToString("dd/MM/yyyy HH:mm") }       # dirty date format
            $cid = "C{0:D5}" -f $rnd.Next(1,1001)
            if ($rnd.Next(0,100) -lt 1) { $cid = "" }                                         # dirty: missing customer
            $qty = $rnd.Next(1,8)
            if ($rnd.Next(0,1000) -lt 5) { $qty = -$qty }                                     # dirty: negative qty
            $price = [math]::Round(5 + $rnd.NextDouble() * 300, 2)
            $disc = @(0,0,0,5,10,15)[$rnd.Next(0,6)]
            $line = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}" -f $oid,$tsText,$cid,("S{0:D2}" -f $rnd.Next(1,21)),("P{0:D4}" -f $rnd.Next(1,201)),$qty,$price,$disc,(Pick $statuses),(Pick $channels),$b
            $lines.Add($line)
            if ($rnd.Next(0,100) -lt 2) { $lines.Add($line) }                                 # dirty: exact duplicate
        }
        if ($b -eq 1) { foreach ($l in $lines) { $batch1Lines.Add($l) } }
        if ($b -eq 3) {
            # late arriving orders (older timestamps, new ids)
            for ($k = 1; $k -le 300; $k++) {
                $orderIdx++
                $ts = (Get-Date "2026-01-01").AddMinutes($rnd.Next(0, 60*24*120))
                $lines.Add(("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}" -f ("O{0:D6}" -f $orderIdx),$ts.ToString("yyyy-MM-ddTHH:mm:ss"),("C{0:D5}" -f $rnd.Next(1,1001)),("S{0:D2}" -f $rnd.Next(1,21)),("P{0:D4}" -f $rnd.Next(1,201)),$rnd.Next(1,8),[math]::Round(5+$rnd.NextDouble()*300,2),0,"shipped","web",3))
            }
            # updates to existing batch1 orders (status change)
            $upd = $batch1Lines | Get-Random -Count 100 -SetSeed $Seed
            foreach ($u in $upd) {
                $p = $u.Split(",")
                $p[8] = "returned"; $p[10] = "3"
                $lines.Add(($p -join ","))
            }
        }
        $w = New-Writer (Join-Path $DataDir ("orders\orders_batch_{0}.csv" -f $b))
        $w.WriteLine("order_id,order_ts,customer_id,store_id,product_id,quantity,unit_price,discount_pct,status,channel,ingestion_batch")
        foreach ($l in $lines) { $w.WriteLine($l) }
        $w.Close()
    }

    # ---- telemetry.jsonl ----
    $w = New-Writer (Join-Path $DataDir "telemetry\telemetry.jsonl")
    $t0 = Get-Date "2026-06-01T00:00:00"
    $prev = $null
    for ($i = 0; $i -lt 20000; $i++) {
        $dev = "dev-{0:D3}" -f $rnd.Next(1,51)
        $ts = $t0.AddSeconds($i * 3 + $rnd.Next(0,3)).ToString("yyyy-MM-ddTHH:mm:ss")
        $temp = [math]::Round(18 + $rnd.NextDouble() * 12, 2)
        if ($rnd.Next(0,100) -lt 1) { $temp = -999 }                                          # sentinel
        $hum = [math]::Round(30 + $rnd.NextDouble() * 50, 1)
        $st = Pick @("ok","ok","ok","warn","error")
        $line = '{{"device_id":"{0}","ts":"{1}","temperature":{2},"humidity":{3},"status":"{4}","firmware":"{5}"}}' -f $dev,$ts,$temp,$hum,$st,(Pick @("1.0.2","1.0.3","1.1.0"))
        $roll = $rnd.Next(0,100)
        if ($roll -lt 1) { $line = $line.Substring(0, $line.Length - 10) }                    # broken JSON
        elseif ($roll -lt 2) { $line = '{{"device_id":"{0}","ts":"{1}"}}' -f $dev,$ts }       # missing fields
        $w.WriteLine($line)
        if ($rnd.Next(0,100) -lt 1) { $w.WriteLine($line) }                                   # duplicate
    }
    $w.Close()

    # ---- small files for compaction lab ----
    for ($f = 1; $f -le 100; $f++) {
        $w = New-Writer (Join-Path $DataDir ("small_files\part_{0:D3}.csv" -f $f))
        $w.WriteLine("id,value,event_date")
        for ($r = 1; $r -le 20; $r++) {
            $w.WriteLine(("{0},{1},{2}" -f (($f*100)+$r), $rnd.Next(1,1000), (Get-Date "2026-06-01").AddDays($rnd.Next(0,30)).ToString("yyyy-MM-dd")))
        }
        $w.Close()
    }

    @"
# Data dictionary
- customers/customers_day1.csv, customers_day2.csv : customer master (day2 = changes + new customers) -> SCD2 lab
- products/products.csv : product master
- stores/stores.csv : store master
- orders/orders_batch_1..3.csv : transactions, 3 batches (batch 3 has late-arriving rows and updates)
- telemetry/telemetry.jsonl : IoT events (JSON lines)
- small_files/ : 100 tiny CSV files (compaction lab)
Data quality issues are planted deliberately. Finding them is part of the exercise.
"@ | Set-Content -Path (Join-Path $DataDir "DATA_DICTIONARY.md") -Encoding UTF8

    Write-Host "Data generated." -ForegroundColor Green
}

New-LabData

if ($SkipFabric) {
    Write-Host "`n-SkipFabric used. Upload the 'data' folder to your Lakehouse Files manually (or run again without the switch)." -ForegroundColor Yellow
    return
}

# ---------------------------------------------------------------------------
# 2. Prerequisites: Azure CLI + login
# ---------------------------------------------------------------------------
Write-Step "Checking Azure CLI"
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    $ans = Read-Host "Azure CLI not found. Install via winget now? (y/n)"
    if ($ans -eq "y") {
        winget install --id Microsoft.AzureCLI -e --accept-source-agreements --accept-package-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        Write-Warning "Azure CLI still not available. Restart PowerShell after installing, or use -SkipFabric."
        return
    }
}

$acct = $null
try { $acct = az account show 2>$null | ConvertFrom-Json } catch {}
if (-not $acct) {
    Write-Step "Signing in (a browser window will open)"
    az login --allow-no-subscriptions | Out-Null
}

function Get-Token($resource) {
    $t = az account get-access-token --resource $resource --query accessToken -o tsv
    if (-not $t) { throw "Could not get token for $resource" }
    return $t
}

function Invoke-Fabric($Method, $Path, $Body = $null) {
    $headers = @{ Authorization = "Bearer $(Get-Token 'https://api.fabric.microsoft.com')" }
    $uri = "$FabricApi$Path"
    if ($null -ne $Body) {
        return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 8)
    }
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
}

# ---------------------------------------------------------------------------
# 3. Workspace + capacity + lakehouse
# ---------------------------------------------------------------------------
Write-Step "Workspace '$WorkspaceName'"
$ws = (Invoke-Fabric Get "/workspaces").value | Where-Object { $_.displayName -eq $WorkspaceName } | Select-Object -First 1
if (-not $ws) {
    $ws = Invoke-Fabric Post "/workspaces" @{ displayName = $WorkspaceName }
    Write-Host "Created workspace $($ws.id)"
} else {
    Write-Host "Reusing workspace $($ws.id)"
}

if (-not $ws.capacityId -or $CapacityId) {
    if (-not $CapacityId) {
        $caps = (Invoke-Fabric Get "/capacities").value | Where-Object { $_.state -eq "Active" }
        if (-not $caps) { throw "No active Fabric capacity found. Start a Trial or pass -CapacityId." }
        $CapacityId = ($caps | Select-Object -First 1).id
        Write-Host "Using capacity: $(($caps | Select-Object -First 1).displayName)"
    }
    Invoke-Fabric Post "/workspaces/$($ws.id)/assignToCapacity" @{ capacityId = $CapacityId } | Out-Null
}

Write-Step "Lakehouse '$LakehouseName'"
function Find-Lakehouse {
    return (Invoke-Fabric Get "/workspaces/$($ws.id)/lakehouses").value | Where-Object { $_.displayName -eq $LakehouseName } | Select-Object -First 1
}
$lh = Find-Lakehouse
if (-not $lh) {
    try { Invoke-Fabric Post "/workspaces/$($ws.id)/lakehouses" @{ displayName = $LakehouseName } | Out-Null } catch { Write-Warning $_.Exception.Message }
    for ($i = 0; $i -lt 30 -and -not $lh; $i++) { Start-Sleep -Seconds 4; $lh = Find-Lakehouse }
    if (-not $lh) { throw "Lakehouse was not created. Check capacity and permissions." }
}
Write-Host "Lakehouse id: $($lh.id)"

# ---------------------------------------------------------------------------
# 4. Upload data to OneLake (ADLS Gen2 REST: create -> append -> flush)
# ---------------------------------------------------------------------------
function Send-OneLakeFile($Token, $Url, $LocalPath) {
    $h = @{ Authorization = "Bearer $Token"; "x-ms-version" = "2021-06-08" }
    $bytes = [System.IO.File]::ReadAllBytes($LocalPath)
    Invoke-RestMethod -Method Put -Uri "${Url}?resource=file" -Headers $h | Out-Null
    if ($bytes.Length -gt 0) {
        Invoke-RestMethod -Method Patch -Uri "${Url}?action=append&position=0" -Headers $h -Body $bytes -ContentType "application/octet-stream" | Out-Null
    }
    Invoke-RestMethod -Method Patch -Uri "${Url}?action=flush&position=$($bytes.Length)" -Headers $h | Out-Null
}

Write-Step "Uploading data to OneLake (Files/raw/...)"
$storageToken = Get-Token "https://storage.azure.com"
$base = "$OneLakeHost/$($ws.id)/$($lh.id)/Files/raw"
$files = Get-ChildItem -Path $DataDir -Recurse -File | Where-Object { $_.Extension -in ".csv",".jsonl" }
$n = 0
foreach ($f in $files) {
    $rel = $f.FullName.Substring($DataDir.Length + 1).Replace("\", "/")
    try {
        Send-OneLakeFile $storageToken "$base/$rel" $f.FullName
        $n++
        if ($n % 20 -eq 0) { Write-Host "  uploaded $n / $($files.Count)" }
    } catch {
        Write-Warning "Upload failed for $rel : $($_.Exception.Message)"
    }
}
Write-Host "Uploaded $n files." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 5. Save config
# ---------------------------------------------------------------------------
$cfg = [ordered]@{
    workspaceName = $WorkspaceName; workspaceId = $ws.id
    lakehouseName = $LakehouseName; lakehouseId = $lh.id
    capacityId = $CapacityId
    onelakePath = "abfss://$($ws.id)@onelake.dfs.fabric.microsoft.com/$($lh.id)/Files/raw"
}
$cfg | ConvertTo-Json | Set-Content -Path (Join-Path $Root "lab-config.json") -Encoding UTF8

Write-Host "`nDone. Open the workspace in https://app.fabric.microsoft.com and check Lakehouse > Files > raw." -ForegroundColor Green
Write-Host "Config saved to lab-config.json. Next: read 00-Cheatsheet.md, then do 02-MCQ-50.md." -ForegroundColor Green
