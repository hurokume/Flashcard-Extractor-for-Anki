@echo off
setlocal enabledelayedexpansion
set /p "input_dir=変換したいPDFファイルが存在するディレクトリのパスを入力してください: "

where gswin64c >nul 2>nul
if errorlevel 1 (
    for /d %%d in ("C:\Program Files\gs\gs*") do (
        if exist "%%~fd\bin\gswin64c.exe" (
            set "PATH=%%~fd\bin;%PATH%"
            goto :gs_found
        )
    )
    for /d %%d in ("C:\Program Files (x86)\gs\gs*") do (
        if exist "%%~fd\bin\gswin64c.exe" (
            set "PATH=%%~fd\bin;%PATH%"
            goto :gs_found
        )
    )
)

:gs_found
where gswin64c >nul 2>nul
if errorlevel 1 (
    echo Ghostscript が見つかりません。PDF変換には gswin64c.exe が必要です。
    echo 例: winget install ArtifexSoftware.GhostScript
    exit /b 1
)

if not exist "%input_dir%" (
    echo 指定されたディレクトリが存在しません: "%input_dir%"
    exit /b 1
)

pushd "%input_dir%" >nul 2>nul
if errorlevel 1 (
    echo ディレクトリに移動できませんでした: "%input_dir%"
    exit /b 1
)

set "found_pdf=0"
set "had_error=0"
for %%f in (*.pdf) do (
    set "found_pdf=1"
    set "pdf_file=%%~ff"
    set "base_name=%%~nf"
    set "page_count="

    for /f %%p in ('magick identify -ping -format "1\n" "%%~ff" 2^>nul ^| find /c "1"') do set "page_count=%%p"

    if not defined page_count (
        echo ページ数の取得に失敗しました: "%%~ff"
        echo Ghostscript または PDF delegate の設定を確認してください。
        set "had_error=1"
    ) else (
        echo 変換開始: "%%~nxf" （!page_count!ページ）
        for /l %%i in (1,1,!page_count!) do (
            set /a page_index=%%i-1
            set "page_num=00%%i"
            set "output_file=!base_name!_page!page_num:~-3!.png"

            if exist "!output_file!" (
                echo "!output_file!" already exists. Skipping page %%i
            ) else (
                magick -density 300 "%%~ff[!page_index!]" "!output_file!"
                if errorlevel 1 (
                    echo 変換に失敗しました: "%%~ff" page %%i
                    set "had_error=1"
                )
            )
        )
    )
)

if "%found_pdf%"=="0" (
    echo PDFファイルが見つかりませんでした: "%input_dir%"
    popd
    exit /b 1
)

popd
if "%had_error%"=="1" exit /b 1