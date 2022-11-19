import subprocess

command = 'pip install -r requirements.txt'
result = subprocess.run(command, shell=True)
print(result)
if result.returncode == 0:
    print("Successful Installed")
else:
    print("呜呜呜，没有装上，好可怜")