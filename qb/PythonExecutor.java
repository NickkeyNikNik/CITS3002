import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class PythonExecutor {

    private static final String PYTHON_EXECUTABLE = "/usr/bin/python3"; // NOTE: must be set to local python instance path

    public static String executePython(String pythonFunction, ArrayList<String> args, String functionName) throws IOException {
        /*
         * Executes Python program and returns the result as a String.
         * Returns empty string if code crashes.
         * 
         * args:
         *      pythonFunction: String of entire raw code of Python function.
         *      args: Array of args for function.
         *      functionName: Name of function to run.
         * 
         * returns:
         *      String: output of function formatted by print().
         */

        pythonFunction += "\nprint(" +
            functionName +
            "(" + String.join(",", args) + "))\n";

        List<String> command = new ArrayList<>();
        command.add(PYTHON_EXECUTABLE);
        command.add("-c");
        command.add(pythonFunction);

        command.addAll(args);

        ProcessBuilder processBuilder = new ProcessBuilder(command);
        Process process = processBuilder.start();

        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String line;
        StringBuilder outputBuilder = new StringBuilder();
        while ((line = reader.readLine()) != null) {
            outputBuilder.append(line);
        }
        return outputBuilder.toString();
    }

    public static void main(String[] args) {
        String pythonFunction = "def test(x, y):\n" +
                                "    return x + y\n";
        ArrayList<String> functionInputs = new ArrayList<>();
        functionInputs.add("3");
        functionInputs.add("4");
        try {
            System.out.println(executePython(
                pythonFunction,
                functionInputs,
                "test"
            ));
        } catch (IOException e) {
            System.out.println(e);
        }
    }
}
