import java.io.*;
import java.lang.reflect.Array;
import java.net.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Scanner;
import java.util.Random;

public class qbServer {
 
    private static Socket clientSocket = null;
    private static ServerSocket server = null;
    private static ArrayList<String> multiQuestions;
    private static ArrayList<String> multiAnswers;
    private static ArrayList<String> codeQuestions;
    private static ArrayList<String> codeFunctionNames;
    private static ArrayList<String> codeArgs;
    private static ArrayList<String> codeAnswers;
    private static ArrayList<String> codeOutTypes;
    private static PythonExecutor pythonExecutor = new PythonExecutor();
    private static CExecutor cExecutor = new CExecutor();
    private static int EXECUTOR_TYPE; // 1: C, 2: Python

    public static ArrayList<String> readFile(String filePath)
    {
        /*
         * Reads file by line and splits into ArrayList<String>.
         * 
         * args:
         *      filePath: Path to input file.
         * 
         * returns:
         *      ArrayList<String>: Lines in file.
         */
        try {
            ArrayList<String> lines = new ArrayList<String>();
            Scanner sc;
            sc = new Scanner(new FileReader(filePath));
            String line;
            while(sc.hasNextLine()) {
                line = sc.nextLine();
                lines.add(line);
            }
            return lines;
        } catch (FileNotFoundException e) {
            System.out.println(e);
            return new ArrayList<String>();
        }
    }

    public static void sendMessage(String message) throws IOException
    {
        /*
         * Sends message to clientSocket.
         * 
         * args:
         *      message: String of message to send.
         */
        OutputStream outStream = clientSocket.getOutputStream();
        byte[] messageBytes = message.getBytes();
        outStream.write(messageBytes);
    }

    public static ArrayList<String> getRandomItems(ArrayList<String> list, int numItems, int prefix)
    {
        ArrayList<String> listCopy = new ArrayList<>(list);
        Random rand = new Random();
        ArrayList<String> newList = new ArrayList<>();

        for (int i = 0; i < listCopy.size(); i++)
        {
            listCopy.set(i, String.format("%01d%s%s", prefix, String.format("%02d", i), listCopy.get(i)));
        }


        for (int i = 0; i < numItems; i++) {
            int randomIndex = rand.nextInt(listCopy.size());
             newList.add(listCopy.get(randomIndex));
             listCopy.remove(randomIndex);
        }
        return newList;
    }

    public static void getQuestions(int numQuestions)
    {
        /*
         * Questions are sent prefixed with one int to indicate question typ.
         * Then two digit index.
         */
        ArrayList<String> multiQs = getRandomItems(multiQuestions, numQuestions, 0);
        ArrayList<String> cQs = getRandomItems(codeQuestions, numQuestions, 1);
        ArrayList<String> pyQs = getRandomItems(codeQuestions, numQuestions, 2);
        ArrayList<String> allQs = new ArrayList<String>();
        allQs.addAll(multiQs);
        allQs.addAll(cQs);
        allQs.addAll(pyQs);
        String message = String.format("%s%s", String.join("\0", allQs), "\0");
        try {
            sendMessage(message);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void markMulti(int questionInd, String answer, boolean thirdGuess) throws IOException
    {
        /*
         * Checks response to multiple choice question and sends response to
         * clientSocket in format: TODO:
         * 
         * args:
         *      questionInd: Index of question in multiQuestions.
         *      answer: Answer given by user.
         *      thirdGuess: Flag for sending correct asnwer if incorrect.
         * 
         */
        if (answer.equals(multiAnswers.get(questionInd)))
        {
            sendMessage("1");
        }
        else if (!thirdGuess)
        {
            sendMessage("0");
        }
        else
        {
            sendMessage(multiAnswers.get(questionInd));
        }
    }

    public static void markC (int questionInd, String answer) throws IOException
    {
        ArrayList<ArrayList<String>> args = new ArrayList<ArrayList<String>>();
        ArrayList<String> answers = new ArrayList<String>();
        for (int i = 0; i < codeArgs.size(); i++)
        {
            ArrayList<String> testCase = new ArrayList<String>();
            testCase.addAll(Arrays.asList(codeArgs.get(i).split(",")));
            if (testCase.get(0).equals("" + questionInd))
            {
                testCase.remove(0);
                args.add(testCase);
                answers.add(codeAnswers.get(i));
            }
        }
        String message = "";
        for (int i = 0; i < args.size(); i++)
        {
            message += String.join(",", args.get(i));
            message += "\0";
            String[] testCaseArgs = new String[args.get(i).size()];
            testCaseArgs = args.get(i).toArray(testCaseArgs);
            String response = "";
            try {
                response  = CExecutor.executeC(answer, testCaseArgs, codeFunctionNames.get(questionInd), codeOutTypes.get(questionInd));
            } catch (IOException e) {
                response = "IOException";
            } catch (RuntimeException e) {
                response = "RuntimeException";
            }
            message += response + "\0";
            message += answers.get(i) + "\0";
        }
        sendMessage(message);
    }

    public static void markPy (int questionInd, String answer) throws IOException
    {
        ArrayList<ArrayList<String>> args = new ArrayList<ArrayList<String>>();
        ArrayList<String> answers = new ArrayList<String>();
        for (int i = 0; i < codeArgs.size(); i++)
        {
            ArrayList<String> testCase = new ArrayList<String>();
            testCase.addAll(Arrays.asList(codeArgs.get(i).split(",")));
            if (testCase.get(0).equals("" + questionInd))
            {
                testCase.remove(0);
                args.add(testCase);
                answers.add(codeAnswers.get(i));
            }
        }
        String message = "";
        for (int i = 0; i < args.size(); i++)
        {
            String response = "";
            message += String.join(",", args.get(i));
            message += "\0";
            try {
                response = PythonExecutor.executePython(answer, args.get(i), codeFunctionNames.get(questionInd));
            } catch (IOException e) {
                response = "IOException";
            } catch (RuntimeException e) {
                response = "RuntimeException";
            }
            message += response + "\0";
            message += answers.get(i) + "\0";
        }
        sendMessage(message);
    }
 
    public qbServer(int port)
    {
        try {
            server = new ServerSocket(port);
 
            System.out.println("Server started");
 
            System.out.println("Waiting for a client ...");
 
            clientSocket = server.accept();
 
            System.out.println("Client accepted");
 
            DataInputStream in = new DataInputStream(new BufferedInputStream(clientSocket.getInputStream()));
  
            String message = "";

            while (!message.equals("EndMessage")) {
                StringBuilder messageBuilder = new StringBuilder();
                int c;
                while ((c = in.read()) != -1 && c != 0) {
                    messageBuilder.append((char) c);
                }
                message = messageBuilder.toString();
                if (message.charAt(0) == '3')
                {
                    getQuestions(10);
                }
                else if (message.charAt(0) == '0') // mark multi
                {
                    int questionsInd = Integer.parseInt(message.substring(1, 3));
                    Boolean thirdGuess = message.charAt(3) == '1';
                    markMulti(questionsInd, message.substring(4, message.length()), thirdGuess);
                }
                else if (message.charAt(0) == '1') // mark C
                {
                    int questionsInd = Integer.parseInt(message.substring(1, 3));
                    markC(questionsInd, message.substring(3, message.length()));
                }
                else if (message.charAt(0) == '2') // mark Python
                {
                    int questionsInd = Integer.parseInt(message.substring(1, 3));
                    markPy(questionsInd, message.substring(3, message.length()));
                }
            }
            in.close();
            server.close();
        }
 
        catch (IOException e) {
            System.out.println(e);
        }
    }
 
    public static void main(String[] args) throws Exception
    {
        int port_num = Integer.parseInt(args[0]);
        EXECUTOR_TYPE = Integer.parseInt(args[1]);
        multiQuestions = readFile(args[2]);
        multiAnswers = readFile(args[3]);
        if (EXECUTOR_TYPE == 1)
        {
            codeQuestions = readFile(args[4]);
            codeFunctionNames = readFile(args[5]);
            codeArgs = readFile(args[6]);
            codeAnswers = readFile(args[7]);
            codeOutTypes = readFile(args[8]);
        }
        else if (EXECUTOR_TYPE == 2)
        {
            codeQuestions = readFile(args[4]);
            codeFunctionNames = readFile(args[5]);
            codeArgs = readFile(args[6]);
            codeAnswers = readFile(args[7]);
        }
        else {throw new Exception("Unrecognised executor type.");}
        qbServer server = new qbServer(port_num);
    }
}
