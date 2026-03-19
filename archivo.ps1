# --- Configuración Inicial ---
$ErrorActionPreference = "Stop"
$currentDir = Get-Location
$fileName = "Arquitectura_RH_Russell_Bedford_V2.pptx"
$outputPath = Join-Path $currentDir $fileName

# Paleta de Colores Russell Bedford (Aproximada)
$ColorBlue   = 0x6D3B12  # Azul Institucional (formato BGR para COM)
$ColorGold   = 0x2A8BD2  # Dorado/Naranja Institucional
$ColorGray   = 0x555555  # Gris para subtítulos
$ColorLight  = 0xFCFAF8  # Fondo claro
$ColorWhite  = 0xFFFFFF

# --- Funciones de Soporte ---

function Add-TextBox {
    param($Slide, [string]$Text, [double]$Left, [double]$Top, [double]$Width, [double]$Height, 
          [int]$FontSize = 18, [bool]$Bold = $false, [int]$Color = 0x1F1F1F, [string]$Align = "Left")

    $shape = $Slide.Shapes.AddTextbox(1, $Left, $Top, $Width, $Height)
    $range = $shape.TextFrame.TextRange
    $range.Text = $Text
    $range.Font.Size = $FontSize
    $range.Font.Bold = [int]$Bold
    $range.Font.Name = "Aptos"
    $range.Font.Color.RGB = $Color
    
    if ($Align -eq "Center") { $shape.TextFrame.TextRange.ParagraphFormat.Alignment = 2 }
    $shape.TextFrame.WordWrap = -1
    return $shape
}

function Add-Header {
    param($Slide, [string]$Title, [string]$Subtitle = "")
    
    # Barra lateral decorativa
    $rect = $Slide.Shapes.AddShape(1, 0, 20, 15, 60)
    $rect.Fill.ForeColor.RGB = $ColorGold
    $rect.Line.Visible = 0

    Add-TextBox -Slide $Slide -Text $Title -Left 30 -Top 20 -Width 900 -Height 40 -FontSize 32 -Bold $true -Color $ColorBlue | Out-Null
    if ($Subtitle) {
        Add-TextBox -Slide $Slide -Text $Subtitle -Left 32 -Top 65 -Width 880 -Height 30 -FontSize 14 -Color $ColorGray | Out-Null
    }
    # Línea divisora
    $line = $Slide.Shapes.AddShape(1, 30, 105, 890, 2)
    $line.Fill.ForeColor.RGB = 0xEEEEEE
    $line.Line.Visible = 0
}

function Add-ModernTable {
    param($Slide, [string]$Title, [object[]]$Rows, [double]$Left, [double]$Top, [double]$Width)
    
    Add-TextBox -Slide $Slide -Text $Title -Left $Left -Top ($Top - 30) -Width $Width -Height 25 -FontSize 16 -Bold $true -Color $ColorBlue | Out-Null
    
    $tableShape = $Slide.Shapes.AddTable($Rows.Count + 1, 3, $Left, $Top, $Width, ($Rows.Count * 30))
    $table = $tableShape.Table

    $headers = @("Campo", "Ejemplo (Prueba)", "Descripción / Significado")
    for ($col = 1; $col -le 3; $col++) {
        $cell = $table.Cell(1, $col).Shape
        $cell.Fill.ForeColor.RGB = $ColorBlue
        $text = $cell.TextFrame.TextRange
        $text.Text = $headers[$col - 1]
        $text.Font.Bold = -1
        $text.Font.Size = 12
        $text.Font.Color.RGB = $ColorWhite
    }

    for ($i = 0; $i -lt $Rows.Count; $i++) {
        $data = $Rows[$i]
        $vals = @($data.Campo, $data.Ejemplo, $data.Significado)
        for ($col = 1; $col -le 3; $col++) {
            $cell = $table.Cell($i + 2, $col).Shape
            $cell.TextFrame.TextRange.Text = [string]$vals[$col - 1]
            $cell.TextFrame.TextRange.Font.Size = 10
            $cell.Fill.ForeColor.RGB = if ($i % 2 -eq 0) { 0xFFFFFF } else { 0xF9F9F9 }
        }
    }
}

# --- Ejecución Principal ---

Write-Host "Iniciando creación de presentación..." -ForegroundColor Cyan

$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Add()
$pres.PageSetup.SlideWidth = 960
$pres.PageSetup.SlideHeight = 540

try {
    # Diapositiva 1: Portada
    $slide = $pres.Slides.Add(1, 12)
    $bg = $slide.Shapes.AddShape(1, 0, 0, 960, 540)
    $bg.Fill.ForeColor.RGB = $ColorBlue
    Add-TextBox -Slide $slide -Text "ARQUITECTURA DE DATOS" -Left 0 -Top 180 -Width 960 -Height 50 -FontSize 44 -Bold $true -Color $ColorWhite -Align "Center" | Out-Null
    Add-TextBox -Slide $slide -Text "Gestión de Recursos Humanos | Russell Bedford" -Left 0 -Top 240 -Width 960 -Height 40 -FontSize 20 -Color $ColorGold -Align "Center" | Out-Null
    Add-TextBox -Slide $slide -Text "Modelo de Datos Escalable y Normalizado" -Left 0 -Top 480 -Width 960 -Height 30 -FontSize 12 -Color $ColorWhite -Align "Center" | Out-Null

    # Diapositiva 2: Tabla DAT_EMPLEADO_PER
    $slide = $pres.Slides.Add(2, 12)
    Add-Header -Slide $slide -Title "Entidad: Datos Personales" -Subtitle "Tabla [DAT_EMPLEADO_PER] - Información biográfica estable"
    $rows = @(
        @{ Campo = "ID_EMPLEADO_PER"; Ejemplo = "EMP-P001"; Significado = "PK: Identificador único personal" },
        @{ Campo = "CC"; Ejemplo = "1.088.123.456"; Significado = "Documento de Identidad" },
        @{ Campo = "NOM_EMPLEADO"; Ejemplo = "Carlos"; Significado = "Nombres del colaborador" },
        @{ Campo = "APE_EMPLEADO"; Ejemplo = "Restrepo"; Significado = "Apellidos del colaborador" },
        @{ Campo = "CORREO"; Ejemplo = "c.restrepo@email.com"; Significado = "Correo electrónico personal" },
        @{ Campo = "FECHA_NAC"; Ejemplo = "1990-05-20"; Significado = "Fecha de nacimiento" }
    )
    Add-ModernTable -Slide $slide -Title "Estructura de la Tabla" -Rows $rows -Left 50 -Top 150 -Width 860

    # Diapositiva 3: Tabla DAT_EMPLEADO_COR (El Corazón)
    $slide = $pres.Slides.Add(3, 12)
    Add-Header -Slide $slide -Title "Entidad: Núcleo Corporativo" -Subtitle "Tabla [DAT_EMPLEADO_COR] - Vinculación operativa"
    $rowsCor = @(
        @{ Campo = "ID_EMPLEADO"; Ejemplo = "RB-2024-01"; Significado = "ID de empleado en la firma" },
        @{ Campo = "FK_ID_PER"; Ejemplo = "EMP-P001"; Significado = "Relación con Datos Personales" },
        @{ Campo = "FK_ID_PUESTO"; Ejemplo = "ROI-05"; Significado = "Relación con Catálogo de Puestos" },
        @{ Campo = "FK_ID_AREA"; Ejemplo = "AREA-FIN"; Significado = "Relación con Unidad de Negocio" },
        @{ Campo = "EMAIL_CORP"; Ejemplo = "c.restrepo@russell.co"; Significado = "Correo institucional asignado" },
        @{ Campo = "ESTATUS"; Ejemplo = "Activo"; Significado = "Estado laboral actual" }
    )
    Add-ModernTable -Slide $slide -Title "Relaciones y Llaves Foráneas" -Rows $rowsCor -Left 50 -Top 150 -Width 860

    # Diapositiva 4: Conclusiones
    $slide = $pres.Slides.Add(4, 12)
    Add-Header -Slide $slide -Title "Beneficios del Modelo" -Subtitle "Por qué implementar esta estructura"
    $bulletPoints = @(
        "Integridad de Datos: La información personal no se duplica.",
        "Mantenimiento Ágil: Cambiar un nombre de área afecta a todos automáticamente.",
        "Escalabilidad: Preparado para auditorías y reportes masivos (Power BI).",
        "Seguridad: Permite separar datos sensibles de datos operativos."
    )
    $box = $slide.Shapes.AddShape(1, 50, 150, 860, 250)
    $box.Fill.ForeColor.RGB = 0xF9F9F9
    $box.Line.ForeColor.RGB = $ColorBlue
    $box.TextFrame.TextRange.Text = ($bulletPoints -join "`r")
    $box.TextFrame.TextRange.Font.Color.RGB = 0x333333
    $box.TextFrame.TextRange.Font.Size = 20
    $box.TextFrame.TextRange.ParagraphFormat.Bullet.Visible = -1

    # Guardar y Cerrar
    $pres.SaveAs($outputPath)
    Write-Host "Presentación creada con éxito en: $outputPath" -ForegroundColor Green

} catch {
    Write-Error "Error durante la creación: $($_.Exception.Message)"
} finally {
    if ($pres) { $pres.Close() }
    $ppt.Quit()
    # Liberar memoria de objetos COM
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}