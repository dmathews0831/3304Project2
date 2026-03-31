import subprocess
import os
import sys
import argparse


def main(args):
    haskel_fname = args.haskell_file

    tests1 = ["0 58 4 97 86 + 20 - * 87 * 65 0 * *  / /",
              "32 40 + 69 40 94 - 19 / 71 86 * 71 * * -", "38 72 49 + + +"]
    oracles1 = ["ERROR: Division by zero",
                "ERROR: Too few operations", "ERROR: Too few operands"]

    tests2 = ["24 22 / 4 - 31 3 * 63 / 92 / - 43 -",
              "85 58 4 97 86 + 20 - * 87 * 65 84 * +  / +",
              "16 52 28 * 16 70 / 52 / 14 / / -",
              "57 92 / 75 16 / 64 / 57 * + 68  -",
              "32 40 + 69 40 94 - 19 / 71 86 * 71 * * -  -"]
    oracles2 = ["-45.925137",
                "85.00093",
                "-4637344.0",
                "-63.20563",
                "-1232123.5"]

    tests3 = ["5 3 + 2 *",
              "10 5 / 3 4 + *"]
    oracles3 = ["16.0",
                "14.0"]

    tests = tests2 + tests1 + tests3
    oracles = oracles2 + oracles1 + oracles3

    score = 0
    test_weights = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]  # Total = 50
    total = sum(test_weights)

    # Get base name without extension
    base_name = os.path.splitext(haskel_fname)[0]
    
    # Determine executable name based on platform
    if sys.platform == "win32":
        executable_name = base_name + ".exe"
    else:
        executable_name = base_name
    
    for i in range(len(tests)):
        test = tests[i]
        orc = oracles[i]

        input_fname = ".input"
        output_fname = ".output"

        with open(input_fname, "w") as f:
            f.write(test)
            f.write("\n")

        # Remove compilation artifacts if they exist
        artifacts = [executable_name, base_name + ".hi", base_name + ".o"]
        for artifact in artifacts:
            if os.path.exists(artifact):
                try:
                    os.remove(artifact)
                except OSError:
                    pass

        # Compile Haskell file
        try:
            result = subprocess.run(
                ["ghc", haskel_fname],
                capture_output=True,
                text=True,
                check=False
            )
            output = result.stdout + result.stderr
        except FileNotFoundError:
            print("Error: GHC (Glasgow Haskell Compiler) not found. Please install GHC and add it to PATH.")
            exit(1)

        if "Compiling" not in output and "Linking" not in output:
            print(output)
            exit(0)

        # Run the compiled executable
        result_output = ""
        program_crashed = False
        error_message = ""
        
        try:
            result = subprocess.run(
                [os.path.join(".", executable_name), input_fname, output_fname],
                capture_output=True,
                text=True,
                check=False,
                timeout=5  # 5 second timeout to prevent hanging
            )
            
            # Check if program had a non-zero exit code
            if result.returncode != 0:
                program_crashed = True
                error_message = f"Program exited with code {result.returncode}"
                if result.stderr:
                    error_message += f"\nStderr: {result.stderr.strip()}"
                if result.stdout:
                    error_message += f"\nStdout: {result.stdout.strip()}"
                    
        except subprocess.TimeoutExpired:
            program_crashed = True
            error_message = "Program exceeded 5 second timeout (possible infinite loop)"
        except FileNotFoundError:
            print(f"Error: Compiled executable '{executable_name}' not found.")
            exit(1)
        except Exception as e:
            program_crashed = True
            error_message = f"Unexpected error running program: {str(e)}"

        # Try to read output file if it exists
        if os.path.exists(output_fname):
            try:
                with open(output_fname) as f:
                    result_output = f.readline().strip()
            except Exception as e:
                if not program_crashed:
                    program_crashed = True
                    error_message = f"Error reading output file: {str(e)}"
        elif not program_crashed:
            program_crashed = True
            error_message = "Output file was not created"

        # Evaluate test result
        if program_crashed:
            print(f"Test {i+1} => 0/{test_weights[i]} | Test Case: {test}")
            print(f"  PROGRAM CRASHED: {error_message}")
            print(f"  Expected Output: {orc}")
        elif result_output.lower() == orc.lower():
            score += test_weights[i]
            print(
                f"Test {i+1} => {test_weights[i]}/{test_weights[i]} | Test Case: {test} | Student Output: {result_output} | Expected Output: {orc}")
        else:
            print(
                f"Test {i+1} => 0/{test_weights[i]} | Test Case: {test} | Student Output: {result_output} | Expected Output: {orc}")

    print(f"\nTotal Score: {score}/{total}")

    # Cleanup
    cleanup_files = [input_fname, output_fname] + artifacts
    for file in cleanup_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                pass


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='A Python autograder to grade Haskell project 2', allow_abbrev=True)
    parser.add_argument('--haskell_file', type=str,
                        help='name of the haskell file to grade (Example cal.hs)', required=True)

    cargs = parser.parse_args()
    assert cargs.haskell_file.endswith(".hs")

    return cargs


if __name__ == "__main__":
    main(parse_arguments())
