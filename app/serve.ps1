# AX-Synth Web Editor: a tiny local web server using only Windows PowerShell
# (no Python or other install needed). Serves this folder on
# http://localhost:8765 (this computer only) and opens it in Microsoft Edge.
# Web MIDI with SysEx needs a secure page address; http://localhost counts as one.
# Start it by double-clicking Start-AX-Synth-Editor.bat. Close the window to stop.
param([int]$Port = 8765, [switch]$NoBrowser)

$root = [System.IO.Path]::GetFullPath((Split-Path -Parent $MyInvocation.MyCommand.Path))
$url = "http://localhost:$Port/"
$types = @{
  '.html' = 'text/html; charset=utf-8'; '.js' = 'text/javascript; charset=utf-8'; '.mjs' = 'text/javascript; charset=utf-8'
  '.json' = 'application/json'; '.css' = 'text/css; charset=utf-8'; '.svg' = 'image/svg+xml'; '.png' = 'image/png'; '.ico' = 'image/x-icon'
}

function Open-Editor {
  if ($NoBrowser) { return }
  try { Start-Process 'msedge' $url -ErrorAction Stop } catch { Start-Process $url }
}

try {
  $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
  $listener.Start()
} catch {
  Write-Host "Port $Port is busy: the editor is probably already running. Opening it."
  Open-Editor
  exit 0
}

Write-Host ""
Write-Host "  AX-Synth Web Editor is running at $url"
Write-Host "  Keep this window open while you use the editor. Close it to stop."
Write-Host ""
Open-Editor

while ($true) {
  $client = $listener.AcceptTcpClient()
  try {
    $stream = $client.GetStream()
    $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::ASCII, $false, 8192, $true)
    $line = $reader.ReadLine()
    while ($true) { $h = $reader.ReadLine(); if ($null -eq $h -or $h -eq '') { break } }
    $method = 'GET'; $path = '/'
    if ($line -match '^(GET|HEAD) (\S+)') { $method = $Matches[1]; $path = $Matches[2] }
    $path = [Uri]::UnescapeDataString(($path -split '\?')[0])
    if ($path -eq '/') { $path = '/index.html' }
    $file = [System.IO.Path]::GetFullPath((Join-Path $root ($path.TrimStart('/'))))
    if ($file.StartsWith($root + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $file -PathType Leaf)) {
      $body = [System.IO.File]::ReadAllBytes($file)
      $type = $types[[System.IO.Path]::GetExtension($file).ToLower()]
      if (-not $type) { $type = 'application/octet-stream' }
      $status = '200 OK'
    } else {
      $body = [System.Text.Encoding]::UTF8.GetBytes('Not found')
      $type = 'text/plain'
      $status = '404 Not Found'
    }
    $head = "HTTP/1.1 $status`r`nContent-Type: $type`r`nContent-Length: $($body.Length)`r`nCache-Control: no-store`r`nConnection: close`r`n`r`n"
    $hb = [System.Text.Encoding]::ASCII.GetBytes($head)
    $stream.Write($hb, 0, $hb.Length)
    if ($method -ne 'HEAD') { $stream.Write($body, 0, $body.Length) }
    $stream.Flush()
  } catch {
    # a browser closed the connection early; ignore and keep serving
  } finally {
    $client.Close()
  }
}
