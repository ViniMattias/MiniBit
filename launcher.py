import os
import platform
import subprocess
import sys

def run_script(script_name: str):
    # Detecta o sistema operacional atual
    system = platform.system()

    if system == "Windows":
        # Monta o caminho e o comando para executar o script PowerShell no Windows
        path = os.path.join("scripts", "windows", f"{script_name}.ps1")
        command = ["powershell", "-ExecutionPolicy", "Bypass", "-File", path]
    elif system in ["Linux", "Darwin"]:
        # Monta o caminho e o comando para executar o script shell no Linux/macOS
        path = os.path.join("scripts", "unix", f"{script_name}.sh")
        os.chmod(path, 0o755)  # garante que o script seja executável
        command = ["bash", path]
    else:
        # Encerra se o sistema operacional não for reconhecido
        sys.exit(1)

    # Verifica se o arquivo de script existe
    if not os.path.exists(path):
        print(f"Script não encontrado: {path}")
        sys.exit(1)

    # Executa o script apropriado
    subprocess.run(command)

if __name__ == "__main__":
    # Verifica se o usuário passou um argumento (nome do script)
    if len(sys.argv) < 2:
        print("Uso: python launcher.py [start_peers | start_tracker | cleanup | stop_all]")
        sys.exit(1)

    # Executa o script correspondente
    run_script(sys.argv[1])
