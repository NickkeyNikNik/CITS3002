import csv
import socket
import os

#0 = connection a
#1 = connection b

HOST = '127.0.0.1'  # localhost
PORT = 3002
CSV_FILE = "users.csv"
# store the login and score details
user_dict = {}
question_dict0 = {}
question_dict1 = {}


# connect to the QB via a port number
def connect_QB(PORT_NUMBER):
    SERVER_ADDRESS = '127.0.0.1'
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_ADDRESS, PORT_NUMBER))
    return client_socket

# poll the QB to mark a question with the student answer, and have it return the answer if this is the student's last attempt
def get_question_marked(QB_CONNECTION, questionID, questionType, studentAnswer, attemptFlag):
    if type == 0:
        get_question_marked_command = f"{questionType}{questionID}{attemptFlag}{studentAnswer}\0"
    else:
        get_question_marked_command = f"{questionType}{questionID}{studentAnswer}\0"
    QB_CONNECTION.sendall(get_question_marked_command.encode())
    print(f"Polled the QB for {questionID} and {studentAnswer} was the given answer and the flag is {attemptFlag}")
    print(f"Our message to the QB is: {get_question_marked_command}")
    question_mark_result = QB_CONNECTION_A.recv(2048).decode()
    response = str(question_mark_result.split("\0"))
    print(f"The response was: {response}")
    return question_mark_result

#store the student's questions in a csv file for future use
def store_dict(username, qbID):
    with open(username + str(qbID) + ".csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if qbID == 0:
            for question in question_dict0:
                info = [question[1:]]
                for key in question_dict0[question]:
                    info.append(question_dict0.get(question)[key])
                writer.writerow(info)
        else:
            for question in question_dict1:
                info = [question[1:]]
                for key in question_dict1[question]:
                    info.append(question_dict1.get(question)[key])
                writer.writerow(info)
                
# read the csv file and store the contents into a question dictionary
def questions_dict(username, qbID):
    with open(username + str(qbID) + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            id = line[0]
            correct = line[1]
            attempts = int(line[2])
            type = line[3]
            name = line[4]
            answer = line[5]
            if qbID == 0:
                question_dict0[type +id] = {'correct':correct, 'attempts':attempts,  'type':type, 'name':name, 'answer':answer}
            else:
                question_dict1[type + id] = {'correct':correct, 'attempts':attempts,  'type':type, 'name':name, 'answer':answer}
        
#read the questions given by the QB and store it into a dictionary, then run store_dict() to store that into the csv file
def store_questions(username, qbID, questions):
    question_list = questions.split("\0")
    correct = "INCORRECT"
    attempts = 3
    answer = " "
    for question in question_list:
        if len(question) > 1:
            print("The question is: " + question + " and the qbID is: " + str(qbID))
            type = question[0]
            id = question[1] + question[2]
            name = question[3:]
            if qbID == 0:
                question_dict0[type + id] = {'correct':correct, 'attempts':attempts,  'type':type, 'name':name, 'answer':answer}   
            else:
                question_dict1[type + id] = {'correct':correct, 'attempts':attempts,  'type':type, 'name':name, 'answer':answer}
    store_dict(username, qbID)

#convert the questions from the dictionary into the html to display to the student
def format_questions(qbID):
    question_number = 1
    formatted_questions = ""
    if(qbID == 0):
        for question_id in question_dict0:
            formatted_question = ""
            question = question_dict0.get(question_id)
            name = question['name']
            type = question['type']
            attempts = question['attempts']
            correct = question['correct']
            answer = question['answer']
            formatted_answer = ""
            if type == "0":
                type = "select"
            else:
                type = "textarea"
            # display an answer section if it's available
            # (which is when the student gets an answer correct or has no more attempts left)
            if answer != " ":
                if answer.startswith("http"):
                    formatted_answer = f'</div><img src="{answer}" alt="answer">'
                elif type != 0:
                    formatted_answer = f'Inputs\tGiven Response\tExpected Response\n{answer}</div>'
                else:
                    formatted_answer = f'The correct answer/output is: {answer}</div>'
            else:
                formatted_answer = ""
            # display question information
            if correct == "CORRECT":
                formatted_question = f'<form name="{name}">' \
                                 f'<div class="question-box">{question_number}. {name} {attempts}/3 CORRECT \n{formatted_answer}'
            elif attempts == 0:
                formatted_question = f'<form name="{name}">' \
                                 f'<div class="question-box">{question_number}. {name} {attempts}/3 INCORRECT \n{formatted_answer}'
            else:
                formatted_question = f'<form name="{name}">' \
                                 f'<div class="question-box">{question_number}. {name} {attempts}/3 \n{formatted_answer}'
            # if the question is multiple choice then create a form with options
            if type == "select":
                formatted_question += f'<select name="" id="{name}">'
                formatted_options = "<option disabled selected value="">----</option>" #either here or the 2nd line below
                for option in ["a", "b", "c", "d"]:
                    formatted_option = f'<option value="{option}">{option}</option>'
                    formatted_options += formatted_option
            # if the question is not multiple choice then create a text box
            else:
                formatted_question += f'<textarea name="" id="{name}" placeholder = "Write Code Here" rows="20" cols="50"></textarea>'
                formatted_options = ''
            submit_button = f'<input type="submit" name="question" value="Submit">'
            formatted_question += f'{formatted_options}{submit_button}</form>'
            formatted_questions += formatted_question
            question_number += 1
    else:
        for question_id in question_dict1:
            formatted_question = ""
            question = question_dict1.get(question_id)
            name = question['name']
            type = question['type']
            attempts = question['attempts']
            correct = question['correct']
            answer = question['answer']
            formatted_answer = ""
            if type == "0":
                type = "select"
            else:
                type = "textarea"
            if answer != " ":
                if answer.startswith("http"):
                    formatted_answer = f'img src="{answer}" alt="answer"'
                elif type != 0:
                    formatted_answer = f'Inputs\tGiven Response\tExpected Response\n{answer}'
                else:
                    formatted_answer = f'The correct answer/output is: {answer}'
            else:
                formatted_answer = ""
            if correct == "CORRECT":
                formatted_question = f'<form name="{name}">' \
                                 f'<div class="question-box">{question_number}. {name} {attempts}/3 CORRECT \n{formatted_answer}</div>'
            elif attempts == 0:
                formatted_question = f'<form name="{name}">' \
                                 f'<div class="question-box">{question_number}. {name} {attempts}/3 INCORRECT \n{formatted_answer}</div>'
            else:
                formatted_question = f'<form name="{name}">' \
                                 f'<div class="question-box">{question_number}. {name} {attempts}/3 \n{formatted_answer}</div>'
            if type == "select":
                formatted_question += f'<select name="" id="{name}">'
                formatted_options = "<option disabled selected value="">----</option>" #either here or the 2nd line below
                for option in ["a", "b", "c", "d"]:
                    formatted_option = f'<option value="{option}">{option}</option>'
                    formatted_options += formatted_option
            else:
                formatted_question += f'<textarea name="" id="{name}" placeholder = "Write Code Here" rows="20" cols="50"></textarea>'
                formatted_options = ''
            submit_button = f'<input type="submit" name="question" value="Submit">'
            formatted_question += f'{formatted_options}{submit_button}</form>'
            formatted_questions += formatted_question
            question_number += 1
    return formatted_questions

#poll the QB for randomised questions
def get_question_set(QB_CONNECTION, username, qbID):
    if os.path.exists(username + str(qbID) + ".csv") == True:
        questions_dict(username, qbID)
    else:
        get_question_command = "3\0"
        QB_CONNECTION.sendall(get_question_command.encode())
        question_set_received = QB_CONNECTION.recv(2048).decode()
        store_questions(username, qbID, question_set_received)
    return format_questions(qbID)

#read the user csv file for login and score information
def read_file():
    with open(CSV_FILE, "r") as csvfile:
        reader = csv.reader(csvfile)

        for line in reader:

            username = line[0]
            password = line[1]
            attempted = line[2]
            score = line[3]

            user_dict[username] = {'password': password, 'attempted': attempted, 'score': score}

#update the user csv file
def write_file():
    with open(CSV_FILE, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        for key in user_dict:
            info = [key]
            for detail in user_dict[key]:
                info.append(user_dict.get(key)[detail])
            writer.writerow(info)

#read the home page template file and fill in the student's details and questions
def format_site(username):
    with open("home.html", "r") as home:
        site = home.read()
        a_question_set = get_question_set(QB_CONNECTION_A, username, 0)
        b_question_set = get_question_set(QB_CONNECTION_B, username, 1)
        site = site.replace("{{username}}", username)
        site = site.replace("{{attempted}}", user_dict.get(username)['attempted'])
        site = site.replace("{{score}}", user_dict.get(username)['score'])
        site = site.replace("{{A_QB_QUESTIONS}}", a_question_set)
        site = site.replace("{{B_QB_QUESTIONS}}", b_question_set)
        site = site.replace("{{SCRIPT}}", f'<script>{open("submit.js").read()}</script>')
        return site

#maintains connection to the website and sends in html to display
#it also retrieves and sends the student's answers for marking and updates relevant dictionaries 
def handle_client_connection(client_socket, QB_CONNECTION_A, QB_CONNECTION_B,  user):
    response = b"HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
    request = client_socket.recv(1024)
    username = ""
    if request.startswith(b"POST /login"):
        #if the student is logging in then check their details, then provide the home page with the student's details
        data = request.split(b"\r\n\r\n")[1]
        username, password = data.decode().split("&")
        username = username.split("=")[1]
        password = password.split("=")[1]
        if username in user_dict and user_dict.get(username)['password'] == password:
            # if login is successful, redirect to home.html with welcome message
            response_body = format_site(username) 
            response = b"HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response_body.encode()
        else:
            response = b"HTTP/1.1 401 Unauthorized\nContent-Type: text/plain\n\nInvalid username or password"
    elif request.startswith(f"GET /127.0.0.1/{PORT}".encode()):
        #retrieve the student's data
        data = request.decode().split('/')[3][:-5]
        datasplit = data.replace("%20", " ").replace("%7B", "{").replace("%7D", "}").split("&")
        print("this is the data" + str(datasplit))
        if(len(datasplit) == 3):       
            #retrieve the question's details including the amount of attempts the student has left
            question, answer, section = datasplit
            correct = ""
            correct_answer = " "
            attempts = 0
            if section == "Question Set A":
                for key in question_dict0:
                    if question_dict0.get(key)['name'] == question:
                        id = key[1:]
                        correct = question_dict0.get(key)['correct']
                        attempts = question_dict0.get(key)['attempts']
                        type = question_dict0.get(key)['type']
            else:
                for key in question_dict1:
                    if question_dict1.get(key)['name'] == question:
                        id = key[1:]
                        correct = question_dict1.get(key)['correct']
                        attempts = question_dict1.get(key)['attempts']
                        type = question_dict1.get(key)['type']
            if(answer != "" and answer !="---" and correct == "INCORRECT" and attempts != 0):
                attempts -=  1
                user_dict.get(user)['attempted'] += 1
                if attempts == 3:
                    attemptFlag = 1
                else:
                    attemptFlag = 0
                #poll the QB
                if section == "Question Set A":
                    answer_status = get_question_marked(QB_CONNECTION_A, id, type, answer, attemptFlag)
                else:
                    answer_status = get_question_marked(QB_CONNECTION_B, id, type, answer, attemptFlag)
                #1 means correct, 0 means incorrect
                #update the relevant dictionaries depending on if the student was correct or incorrect
                if type == 0:
                    if attemptFlag == 1 and answer_status != "1" and answer_status != "0":
                        correct_answer = answer_status
                        if answer == correct_answer:
                            correct = "CORRECT"
                            user_dict.get(user)['score'] += 1
                        else:
                            correct = "INCORRECT"
                    elif answer_status == "1":
                        correct = "CORRECT"
                        user_dict.get(user)['score'] += 1
                else:
                    cases, response, expected_response = answer_status.split('\0')[:-1]
                    if response == expected_response:
                        correct = "CORRECT"
                        user_dict.get(user)['score'] += 1
                    correct_answer = cases + "\t" + response + "\t" + expected_response
                if section == "Question Set A":
                    question_dict0.get(type+id)['correct'] = correct
                    question_dict0.get(type+id)['attempts'] = attempts
                    question_dict0.get(type+id)['answer'] = correct_answer
                    store_dict(user, 0)
                if section == "Question Set B":
                    question_dict1.get(type+id)['correct'] = correct
                    question_dict1.get(type+id)['attempts'] = attempts
                    question_dict1.get(type+id)['answer'] = correct_answer
                    store_dict(user, 1)
                write_file()
                # format the site with updated details
                response_body = format_site(user)
                response = b"HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response_body.encode()
    else:
        response = b"HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + open("login.html", "rb").read()
    client_socket.sendall(response)
    if(username == ""):
        username = user
    return username


if __name__ == '__main__':
    #connect to both sessions of QB
    QB_CONNECTION_A = connect_QB(30002)
    QB_CONNECTION_B = connect_QB(30003)
    read_file()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server listening on port {PORT}...")
    user = ""
    while True:
        client_socket, address = server_socket.accept()
        user = handle_client_connection(client_socket, QB_CONNECTION_A, QB_CONNECTION_B,  user)
        client_socket.close()

