# ocr_text.js for Windows: on-screen text of images with Windows' own OCR (Windows.Media.Ocr: no download, no admin).
#   powershell -NoProfile -ExecutionPolicy Bypass -File ocr_text.ps1 img1.png img2.jpg ...   (OCR_LANGS=th-TH,en-US)
# One JSON line per image, the same shape as ocr_text.js:
#   {"img": path, "w": W, "h": H, "lines": [{"text": s, "conf": 1.0, "box": [x, y, w, h] (pixels, origin top-left)}]}
# Windows OCR gives no confidence (always 1.0). A language works only if Windows has it (Thai: the Thai language pack);
# each image goes through every requested language that's available, and the one that reads the most text wins.
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, [Type]$t) { $task = $asTask.MakeGenericMethod($t).Invoke($null, @($op)); $task.Wait(-1) | Out-Null; $task.Result }
[void][Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
[void][Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics, ContentType = WindowsRuntime]
[void][Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics, ContentType = WindowsRuntime]
[void][Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
[void][Windows.Media.Ocr.OcrResult, Windows.Foundation, ContentType = WindowsRuntime]
[void][Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]

$langs = if ($env:OCR_LANGS) { $env:OCR_LANGS -split ',' } else { @('ru-RU', 'en-US') }
$engines = @(foreach ($c in $langs) {
  $l = New-Object Windows.Globalization.Language($c.Trim())
  if ([Windows.Media.Ocr.OcrEngine]::IsLanguageSupported($l)) { [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($l) }
})
if ($engines.Count -eq 0) { $e = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages(); if ($e) { $engines = @($e) } }
if ($engines.Count -eq 0) { foreach ($path in $args) { [ordered]@{ img = $path; error = 'no OCR language on this Windows' } | ConvertTo-Json -Compress }; exit 0 }

foreach ($path in $args) {
  try {
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path -LiteralPath $path).Path)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $dec = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bmp = Await ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $best = @(); $bestN = -1
    foreach ($eng in $engines) {
      $res = Await ($eng.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
      $lines = @(foreach ($ln in $res.Lines) {
        $r = $ln.Words | ForEach-Object { $_.BoundingRect }
        $x0 = ($r | Measure-Object X -Minimum).Minimum; $y0 = ($r | Measure-Object Y -Minimum).Minimum
        $x1 = ($r | ForEach-Object { $_.X + $_.Width } | Measure-Object -Maximum).Maximum; $y1 = ($r | ForEach-Object { $_.Y + $_.Height } | Measure-Object -Maximum).Maximum
        [ordered]@{ text = $ln.Text; conf = 1.0; box = @([double]$x0, [double]$y0, [double]($x1 - $x0), [double]($y1 - $y0)) }
      })
      $n = ($lines | ForEach-Object { $_.text.Length } | Measure-Object -Sum).Sum
      if ($n -gt $bestN) { $best = $lines; $bestN = $n }
    }
    $stream.Dispose()
    [ordered]@{ img = $path; w = $dec.PixelWidth; h = $dec.PixelHeight; lines = @($best) } | ConvertTo-Json -Compress -Depth 5
  } catch { [ordered]@{ img = $path; error = $_.Exception.Message } | ConvertTo-Json -Compress }
}
