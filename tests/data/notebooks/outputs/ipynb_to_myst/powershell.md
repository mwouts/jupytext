---
kernelspec:
  display_name: PowerShell
  language: PowerShell
  name: powershell
language_info:
  codemirror_mode: powershell
  file_extension: .ps1
  mimetype: text/powershell
  name: PowerShell
  nbconvert_exporter: null
  pygments_lexer: powershell
  version: '5.0'
---

This is an extract from
https://github.com/Jaykul/Jupyter-PowerShell/blob/master/LiterateDevOps.ipynb

```{code-cell} powershell
$imageUrl = 'https://upload.wikimedia.org/wikipedia/commons/2/2f/PowerShell_5.0_icon.png'
$ImageData = @{ "png" = (Invoke-WebRequest $imageUrl -UseBasicParsing).RawContentStream.GetBuffer() }
# $ImageData

Write-Jupyter -InputObject $ImageData -Metadata @{ "image/png" = @{ 'width' = 32 } }
Write-Jupyter -InputObject $ImageData -Metadata @{ "image/png" = @{ 'width' = 64 } }
```
