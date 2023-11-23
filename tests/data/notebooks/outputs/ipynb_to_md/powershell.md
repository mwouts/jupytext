---
jupyter:
  kernelspec:
    display_name: PowerShell
    language: PowerShell
    name: powershell
---

This is an extract from
https://github.com/Jaykul/Jupyter-PowerShell/blob/master/LiterateDevOps.ipynb

```powershell
$imageUrl = 'https://upload.wikimedia.org/wikipedia/commons/2/2f/PowerShell_5.0_icon.png'
$ImageData = @{ "png" = (Invoke-WebRequest $imageUrl -UseBasicParsing).RawContentStream.GetBuffer() }
# $ImageData

Write-Jupyter -InputObject $ImageData -Metadata @{ "image/png" = @{ 'width' = 32 } }
Write-Jupyter -InputObject $ImageData -Metadata @{ "image/png" = @{ 'width' = 64 } }
```
