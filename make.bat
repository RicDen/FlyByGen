@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	@REM adapted sphinx build: use when blender is used and adapter to the path to blender installation
	set SPHINXBUILD= "C://Program Files//Blender Foundation//Blender 3.4//blender.exe" --background --python docs/src/blender_sphinx.py --
	@REM standard sphinx build: use when blender is not part of the tool chain
	@REM set SPHINXBUILD= sphinx-build 
)

set SOURCEDIR=docs/src
set BUILDDIR=Z:/FLYBY_GEN/Docs/build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
