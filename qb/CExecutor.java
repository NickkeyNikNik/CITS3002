import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class CExecutor {

    public static String executeC(String cFunction, String[] args, String functionName, String cOutType) throws IOException, RuntimeException {
        /*
         * Executes C program and returns the result as a String.
         * Throws RuntimeException if C code crashes.
         * 
         * args:
         *      cFunction: String of entire raw code of C function.
         *      args: Array of args for function.
         *      functionName: Name of function to run.
         *      cOutType: String of output type in C.
         * 
         * returns:
         *      String: output of function formatted by printf("%d").
         */

        cFunction += "\n" +
            cOutType + " main(int argc, char* argv[]) {\n" +
            "    printf(\"%d\", " + functionName + "(" + String.join(",", args) + "));\n" +
            "    exit(0);\n" +
            "}\n";

        String compileCommand = "gcc -o cfunction.temp -xc -";

        ProcessBuilder compileProcessBuilder = new ProcessBuilder("bash", "-c", compileCommand);
        Process compileProcess = compileProcessBuilder.start();

        compileProcess.getOutputStream().write(cFunction.getBytes());
        compileProcess.getOutputStream().close();

        try {
            int compileExitCode = compileProcess.waitFor();
            if (compileExitCode != 0) {
                throw new RuntimeException("Compilation failed with exit code " + compileExitCode);
            }
        } catch (InterruptedException e) {
            throw new RuntimeException("Compilation interrupted", e);
        }

        String runCommand = "./cfunction.temp " + String.join(" ", args);

        ProcessBuilder runProcessBuilder = new ProcessBuilder("bash", "-c", runCommand);
        Process runProcess = runProcessBuilder.start();

        BufferedReader reader = new BufferedReader(new InputStreamReader(runProcess.getInputStream()));
        String line;
        StringBuilder outputBuilder = new StringBuilder();
        while ((line = reader.readLine()) != null) {
            outputBuilder.append(line);
        }
        return outputBuilder.toString();
    }

    public static void main(String[] args) throws IOException {
        String cFunction = "int test(int x, int y) {\n" +
                            "    return x + y;\n" +
                            "}";

        String[] inputs = {"3", "4"};

        try {
            System.out.println(
                CExecutor.executeC(cFunction, inputs, "test", "int")
            );
        } catch (RuntimeException e) {
            System.out.println("runtime exception");
        }
    }
}
