import os
import subprocess


def install_gojsonstruct():
    """Install the gojsonstruct tool."""
    try:
        subprocess.run(
            ["go", "install", "github.com/twpayne/go-jsonstruct/v3/cmd/gojsonstruct@latest"], check=True
        )
        print("gojsonstruct installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing gojsonstruct: {e}")


def run_gojsonstruct():
    """Run gojsonstruct with given JSON input."""
    json_input = '{"age":37,"user_height_m":2} {"age":38,"user_height_m":1.7,"favoriteFoods":["cake"]}'

    # Specify the full path to the gojsonstruct binary
    gojsonstruct_path = os.path.expanduser("~/go/bin/gojsonstruct")

    # Construct the command using the full path
    command = f"echo '{json_input}' | {gojsonstruct_path}"

    try:
        # Using shell=True to allow piping with echo
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("gojsonstruct output:", result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running gojsonstruct: {e}, stderr: {e.stderr}")


if __name__ == "__main__":
    install_gojsonstruct()
    result = run_gojsonstruct()
    print("HOLA")
    print(result)
