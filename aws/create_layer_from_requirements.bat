@echo off
set REQUIREMENTS_FILE=requirements.txt

for /f "tokens=*" %%A in (%REQUIREMENTS_FILE%) do (
	rmdir /s %%A
    echo %%A
	mkdir %%A
	cd %%A
	mkdir python
	cd python
	pip install %%A -t .
	cd ..
	cd ..
	powershell Compress-Archive -F %%A/python %%A-layer.zip
	rmdir /s %%A
)
	