import csv
import socket
import os

#0 = connection a
#1 = connection b

HOST = '127.0.0.1'  # localhost
PORT = 3002
CSV_FILE = "users.csv"
user_dict = {}
question_dict0 = {}
question_dict1 = {}



def connect_QB(PORT_NUMBER):
    SERVER_ADDRESS = '127.0.0.1'
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_ADDRESS, PORT_NUMBER))
    return client_socket

def get_question_marked(QB_CONNECTION_A, question, answer):
    get_question_marked_command = f"GET MARKED&{question}&{answer}\0"
    QB_CONNECTION_A.sendall(get_question_marked_command.encode())
    question_mark_result = QB_CONNECTION_A.recv(1024).decode()
    return question_mark_result

def store_dict(username, qbID):
    with open(username + str(qbID) + ".csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if qbID == 0:
            for question in question_dict0:
                info = []
                for key in question_dict0[question]:
                    info.append(question_dict0.get(question)[key])
                writer.writerow(info)
        else:
            for question in question_dict1:
                info = []
                for key in question_dict1[question]:
                    info.append(question_dict1.get(question)[key])
                writer.writerow(info)
                
def questions_dict(username, qbID):
    with open(username + str(qbID) + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        question_number  = 1
        formatted = "["
        for line in reader:
            correct = line[0]
            attempts = int(line[1])
            id = line[2]
            type = line[3]
            name = line[4]
            option1 = line[5]
            option2 = line[6]
            option3 = line[7]
            option4 = line[8]
            if qbID == 0:
                question_dict0[question_number] = {'correct':correct, 'attempts':attempts, 'id':id, 'type':type, 'name':name, 'option1':option1, 'option2':option2, 'option3':option3, 'option4':option4}
            else:
                question_dict1[question_number] = {'correct':correct, 'attempts':attempts, 'id':id, 'type':type, 'name':name, 'option1':option1, 'option2':option2, 'option3':option3, 'option4':option4}
            question_number +=  1
            formatted += name + "," + option1 + "," + option2 + "," + option3 + "," + option4 + ","
        formatted = formatted[:-1]
        formatted += "]"
        return formatted
        
def store_questions(username, qbID, questions):
    sections = 5 #change later with more info from QB
    questions = questions[1:]
    questions = questions[:-1]
    question_list = questions.split(",")
    correct = "INCORRECT"
    attempts = 3
    id = None # add in later
    type = None
    index = 0
    question_number = 1
    for info in question_list:
        if index == 0:
            name = info
        elif index == 1:
            option1 = info
        elif index == 2:
            option2 = info
        elif index == 3:
            option3 = info
        elif index == 4:
            option4 = info
            if qbID == 0:
                question_dict0[question_number] = {'correct':correct, 'attempts':attempts, 'id':id, 'type':type, 'name':name, 'option1':option1, 'option2':option2, 'option3':option3, 'option4':option4}
            else:
                question_dict1[question_number] = {'correct':correct, 'attempts':attempts, 'id':id, 'type':type, 'name':name, 'option1':option1, 'option2':option2, 'option3':option3, 'option4':option4}
            question_number += 1
        if index == 4:
            index = 0
        else:
            index += 1
    store_dict(username, qbID)
    

def get_question_set(QB_CONNECTION, username, qbID):
    question_set_received = ""
    if os.path.exists(username + str(qbID) + ".csv") == True:
        question_set_received = questions_dict(username, qbID)
    else:
        get_question_command = "GET QUESTIONS\0"
        QB_CONNECTION.sendall(get_question_command.encode())
        question_set_received = QB_CONNECTION.recv(1024).decode()
        store_questions(username, qbID, question_set_received)
        question_set_received = questions_dict(username, qbID)
    question_list = question_set_received.split(',')
    edited_question_set = [question_list[i:i + 5] for i in range(0, len(question_list), 5)]
    formatted_questions = ""
    question_number = 1
    for question in edited_question_set:
        question_text = question[0]
        options = question[1:]
        if qbID == 0:
            correct = question_dict0.get(question_number)['correct']
            attempts_per_question = question_dict0.get(question_number)['attempts']
        else:
            correct = question_dict1.get(question_number)['correct']
            attempts_per_question = question_dict1.get(question_number)['attempts']
        if correct == "CORRECT":
            formatted_question = f'<form name="{question_text}">' \
                                 f'<div class="question-box">{question_number}. {question_text} {attempts_per_question}/3 CORRECT</div>' \
                                 f'<select name="" id="{question_text}">'
        elif attempts_per_question == 0:
            formatted_question = f'<form name="{question_text}">' \
                                 f'<div class="question-box">{question_number}. {question_text} {attempts_per_question}/3 INCORRECT</div>' \
                                 f'<select name="" id="{question_text}">'
        else:
            formatted_question = f'<form name="{question_text}">' \
                                 f'<div class="question-box">{question_number}. {question_text} {attempts_per_question}/3</div>' \
                                 f'<select name="" id="{question_text}">'
        formatted_options = "<option disabled selected value="">----</option>"

        for option in options:
            formatted_option = f'<option value="{option}">{option}</option>'
            formatted_options += formatted_option

        # Add submit button for each question
        submit_button = f'<input type="submit" name="question" value="Submit">'

        formatted_question += f'{formatted_options}{submit_button}</form>'
        formatted_questions += formatted_question
        question_number += 1

    formatted_questions = formatted_questions.replace('[', '').replace(']', '')
    return formatted_questions

def check_login(username, password):
    with open(CSV_FILE, "r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == username and row[1] == password:
                return True
        return False

def read_file():
    with open(CSV_FILE, "r") as csvfile:
        reader = csv.reader(csvfile)

        next(reader)

        for line in reader:

            username = line[0]
            password = line[1]
            attempted = line[2]
            score = line[3]
            question_a = line[4]
            question_b = line[5]

            user_dict[username] = {'password': password, 'attempted': attempted, 'score': score, 'question_a': question_a, 'question_b': question_b}


def handle_client_connection(client_socket, QB_CONNECTION_A, QB_CONNECTION_B, site, user):
    response = b"HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
    request = client_socket.recv(1024)
    new_site = ""
    username = ""
    if request.startswith(b"POST /login"):
        data = request.split(b"\r\n\r\n")[1]
        username, password = data.decode().split("&")
        username = username.split("=")[1]
        password = password.split("=")[1]
        if username in user_dict and user_dict.get(username)['password'] == password:
            # if login is successful, redirect to home.html with welcome message
            response_body = open("home.html", "r").read()

            a_question_set = get_question_set(QB_CONNECTION_A, username, 0)
            b_question_set = get_question_set(QB_CONNECTION_B, username, 1)

            response_body = response_body.replace("{{username}}", username)
            response_body = response_body.replace("{{attempted}}", user_dict.get(username)['attempted'])
            response_body = response_body.replace("{{score}}", user_dict.get(username)['score'])
            response_body = response_body.replace("{{A_QB_QUESTIONS}}", a_question_set)
            response_body = response_body.replace("{{B_QB_QUESTIONS}}", b_question_set)
            response_body = response_body.replace("{{SCRIPT}}", f'<script>{open("submit.js").read()}</script>')
            # print(response_body)
            new_site = response_body
            
            response = b"HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response_body.encode()
        else:
            response = b"HTTP/1.1 401 Unauthorized\nContent-Type: text/plain\n\nInvalid username or password"
    elif request.startswith(f"GET /127.0.0.1/{PORT}".encode()):
        # Inside the handle_client_connection function
        data = request.decode().split('/')[3][:-5]
        print("this is the data" + data)
        datasplit = data.replace("%20", " ").split("&")
        response_body = site
        if(len(datasplit) == 3):
            
            question, answer, section = datasplit
            print("The Question is: " + question + " and the answer is: " + answer)
            correct = ""
            attempts = 0
            if section == "Question Set A":
                for key in question_dict0:
                    if question_dict0.get(key)['name'] == question:
                        question_number = key
                        correct = question_dict0.get(key)['correct']
                        attempts = question_dict0.get(key)['attempts']
            else:
                for key in question_dict1:
                    if question_dict1.get(key)['name'] == question:
                        question_number = key
                        correct = question_dict1.get(key)['correct']
                        attempts = question_dict1.get(key)['attempts']
            if(answer != "" and answer !="---" and correct == "INCORRECT" and attempts != 0):
                if section == "Question Set A":
                    answer_status = get_question_marked(QB_CONNECTION_A, question, answer)
                else:
                    answer_status = get_question_marked(QB_CONNECTION_B, question, answer)

                print("The question has been marked\nQuestion:", question, "\nAnswer:", answer, "\nAnswer Status:", answer_status)
                if (attempts != 3):
                    attempts_before = attempts + 1
                else:
                    attempts_before = attempts
                if answer_status == "INCORRECT":
                    attempts -= 1
                    if attempts == 0:
                        #                    f'<div class="question-box">{question_number}. {question_text} {attempts_per_question}/3 INCORRECT</div>' \

                        formatted_question = f'<div class="question-box">{question_number}. {question} {attempts}/3 INCORRECT</div>'
                    else:
                        formatted_question = f'<div class="question-box">{question_number}. {question} {attempts}/3</div>'
                else:
                    correct = "CORRECT"
                    formatted_question = f'<div class="question-box">{question_number}. {question} {attempts}/3 CORRECT</div>'
                #print(formatted_question)
                response_body = response_body.replace(f'<div class="question-box">{question_number}. {question} {attempts_before}/3</div>', formatted_question)
                #print(f'<div class="question-box">{question_number}. {question} {attempts_before}/3</div>')
                if section == "Question Set A":
                    question_dict0.get(question_number)['correct'] = correct
                    question_dict0.get(question_number)['attempts'] = attempts
                    store_dict(user, 0)
                if section == "Question Set B":
                    question_dict1.get(question_number)['correct'] = correct
                    question_dict1.get(question_number)['attempts'] = attempts
                    store_dict(user, 1)
                #print(response_body)
                new_site = response_body
                print(new_site)
                response = b"HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response_body.encode()
                response = b"HTTP/1.1 200 OK\nContent-Type: text/html\n\ntext/plain\n\n Muahahahahahahah!!!"  
    else:
        new_site = open("login.html", "r").read()
        response = b"HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + open("login.html", "rb").read()
    client_socket.sendall(response)
    if(username == ""):
        username = user
    if(new_site == ""):
        return username, site
    return username, new_site



if __name__ == '__main__':
    QB_CONNECTION_A = connect_QB(30002)
    QB_CONNECTION_B = connect_QB(30003)
    read_file()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server listening on port {PORT}...")
    site = ""
    user = ""
    while True:
        client_socket, address = server_socket.accept()
        user, site = handle_client_connection(client_socket, QB_CONNECTION_A, QB_CONNECTION_B, site, user)
        client_socket.close()

