# Render original test text with Windows shaping; no font files are redistributed.
param(
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [Parameter(Mandatory = $true)][string]$TextBase64,
    [ValidateSet('ltr', 'rtl')][string]$Direction = 'ltr'
)

$ErrorActionPreference = 'Stop'
try {
    Add-Type -AssemblyName System.Drawing
} catch {
    Write-Output 'System.Drawing is unavailable.'
    exit 3
}

$bitmap = $null
$graphics = $null
$font = $null
$format = $null
try {
    $text = [System.Text.Encoding]::UTF8.GetString(
        [System.Convert]::FromBase64String($TextBase64)
    )
    $bitmap = [System.Drawing.Bitmap]::new(1600, 800)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.Clear([System.Drawing.Color]::White)
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $font = [System.Drawing.Font]::new(
        'Arial', 64, [System.Drawing.FontStyle]::Regular,
        [System.Drawing.GraphicsUnit]::Pixel
    )
    if ($font.FontFamily.Name -ne 'Arial') {
        Write-Output 'The Arial test font is unavailable.'
        exit 3
    }
    $format = [System.Drawing.StringFormat]::new()
    if ($Direction -eq 'rtl') {
        $format.FormatFlags = [System.Drawing.StringFormatFlags]::DirectionRightToLeft
    }
    $rectangle = [System.Drawing.RectangleF]::new(80, 80, 1440, 640)
    $graphics.DrawString(
        $text, $font, [System.Drawing.Brushes]::Black, $rectangle, $format
    )
    $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Jpeg)
} finally {
    if ($null -ne $format) { $format.Dispose() }
    if ($null -ne $font) { $font.Dispose() }
    if ($null -ne $graphics) { $graphics.Dispose() }
    if ($null -ne $bitmap) { $bitmap.Dispose() }
}
