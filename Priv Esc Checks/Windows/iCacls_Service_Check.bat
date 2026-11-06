@echo off
REM Descripción: Script que consulta todos los servicios y busca ejecutables que otorgan permisos RW al grupo Todos (Everyone).
REM Tipo: Permisos incorrectos de archivos
REM Nota: El carácter ^ escapa caracteres especiales para evitar romper el bucle FOR.
REM Nota: tokens=1* - El valor en el primer delimitador y todo lo que sigue.
for /f "tokens=1*" %%m in ('sc query state^= all ^| find "SERVICE_NAME"') do (
    for /f "tokens=1* delims=: " %%r in ('sc qc "%%~n" ^| find "BINARY_PATH_NAME"') do (
        for /f "delims=" %%x in ('echo(%%~s^| findstr /L /V /I /C:"%SystemRoot%\System32" /C:"%SystemRoot%\SysWOW64"') do (
            icacls "%%~x"
        )
    )
)
