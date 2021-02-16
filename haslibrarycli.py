#!/usr/bin/env python3
#-*- coding: utf-8 -*-

print("Initializing.. Please Wait..")
import urllib, http.cookiejar
import urllib.request
from urllib.request import urlopen
import time
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
from ast import literal_eval
import re
from rich.progress import track
import os
import json

cj = http.cookiejar.LWPCookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)

FAIL_COUNT=0
SUCCESS_COUNT=0
today=datetime.now().strftime("%m/%d/%Y")

def remove():
    print ("\033[A                                                                               \033[A")

def schedule_str_to_code(schedule_array):
    
    global schedule
    new_array=[]
    
    for i in schedule_array:
        temp_array=i.split(' ')
        time=int(temp_array[0].replace("타임",""))
        seatcode=str(temp_array[1].replace("번",""))
        new_array.append((time,seatcode))
        schedule=new_array            
        
    return schedule    

def config_schedule_to_code(schedule_str):
    
    temp_array=schedule_str.split(",")
    schedule=schedule_str_to_code(temp_array)
    return schedule
    
def check_config():
    
    global id,pw,schedule
    global fullpath

    subpath ="HASLIBRARYAPP_Config.json"
    fullpath=os.path.join(os.getenv("LOCALAPPDATA"), subpath) # for WINDOWS
        
    def registration():
        global id,pw,schedule
        id_input=input(" 인트라넷 아이디를 입력하세요: ")
        pw_input=input(" 인트라넷 비밀번호를 입력하세요: ") 
        print("\n 성공적으로 등록이 완료되었습니다. \n 입력한 정보는 본인의 컴퓨터에 안전하게 저장됩니다.")
        print("\n [중요] 메인메뉴에서 3번을 눌러 선호좌석을 등록해주시기 바랍니다.\n 최대 10개의 좌석예약 스케줄을 등록할 수 있으며,\n 기본값은 현재 '1타임 1번' 스케줄 1개가 등록되어있는 상태입니다.")
        print("\033[93m----------------------------------------------------------------\033[0m")
        with open(fullpath, 'w', encoding='ANSI') as config:
            json_data={
                "ID":"%s"%id_input,
                "PW":"%s"%pw_input,
                "SCHEDULE":"1타임 1번"
            }
            json.dump(json_data, config, indent=4,ensure_ascii=False)
        
            id=id_input
            pw=pw_input
            schedule=[(1, '1')]
            return id,pw,schedule
    
    try:
        with open(fullpath, 'rt') as json_file:
            json_data = json.load(json_file)
            id=json_data["ID"]
            pw=json_data["PW"]
            try:
                schedule_temp=json_data["SCHEDULE"]
                schedule=config_schedule_to_code(schedule_temp)
            except KeyError:
                with open(fullpath, 'wt', encoding='ANSI') as config:
                    json_data={
                        "ID":"%s"%id,
                        "PW":"%s"%pw,
                        "SCHEDULE":"1타임 1번"
                    }
                    json.dump(json_data, config, indent=4,ensure_ascii=False)
                schedule=[(1, '1')]
            return id,pw,schedule

    except FileNotFoundError:
        exists = False
        print(" 사용자 설정 파일이 없어서 초기 등록절차를 진행합니다\n")
        registration()    
        
    except:
        print(" Unable to Fetch User Data")
        print(" 기존 파일이 손상되거나 잘못되어 새로 설정 파일을 등록합니다.")
        registration()

    return fullpath
    
def generate_login_token():
    
    global isloginvalid,username
    
    try:
        params = urllib.parse.urlencode({"login_id":id, "login_pw": pw})
        params = params.encode('utf-8')
        # print("Generating Login Token..")
        req = urllib.request.Request("https://hi.hana.hs.kr/proc/login_proc.asp", params)
        response = opener.open(req)
        response = response.read().decode('utf-8')
        
        if "로그인 정보가 잘못되었습니다" in response:
            isloginvalid = False
            print(" \033[31m[CRITICAL ERROR]\033[0m 저장된 로그인 정보가 잘못되었습니다")
            print(" \n 인트라넷 ID, 비밀번호를 수정해주세요")
            print("\033[93m----------------------------------------------------------------\033[0m")
            username="NULL"
            
        else:
            isloginvalid = True
            name_temp=re.compile('<h2>(.*)님 반갑습니다')
            matchobj=name_temp.search(response).group()
            matchobj=matchobj.replace("<h2>","")
            username=matchobj.replace(" 님 반갑습니다","")
            
    except urllib.error.URLError:
        print("\n  \033[31m[ERROR]\033[0m Unable to connect to Intranet Server")
        print("          인터넷 연결을 확인하고 다시 시도해주십시오.\n")
        print("\033[93m----------------------------------------------------------------\033[0m")
        
    except:
        print("\n  \033[31m[ERROR]\033[0m Unable to connect to Intranet Server")
        print("          인터넷 연결을 확인하고 다시 시도해주십시오.\n")
        print("\033[93m----------------------------------------------------------------\033[0m")
        
        
    return isloginvalid,username

def center_window(window,w, h):
    
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    if window == window:
        window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    else:
        window.geometry('%dx%d+%d+%d' % (w, h, x+10, y))

def boldify(str):
    bolded_string = "\033[1m%s\033[0m"%str
    return bolded_string

def timeCodeToString(timecode):
    
    global time_string
    
    if timecode==28:
        time_string="평일 0타임"
    elif timecode == 1:
        time_string="평일 1타임"
    elif timecode == 4:
        time_string="평일 2타임"
    elif timecode == 7:
        time_string="주말 1타임"
    elif timecode == 9:
        time_string="주말 2타임"
    elif timecode == 10:
        time_string="주말 3타임"
    elif timecode == 27:
        time_string="주말 4타임"
    else:
        time_string="(잘못된 타임)"
        
    return time_string

def convert_timecode(timecode_input):
    
    if timecode_input == 1:
        if isweekend()==False:
            timecode=1
        else:
            timecode=7
    elif timecode_input == 2:
        if isweekend()==False:
            timecode=4
        else:
            timecode=9
    elif timecode_input == 0:
        timecode=28
    elif timecode_input == 3:
        timecode=10
    elif timecode_input == 4:
        timecode=27
    else:
        timecode=1000
        
    return timecode

def credentials():

    def center_window(window,w, h):
        
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        if window == window:
            window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        else:
            window.geometry('%dx%d+%d+%d' % (w, h, x+10, y))
            
    from tkinter import Tk, Label, font, Entry, Button, Listbox, INSERT, END, messagebox
    from tkinter.scrolledtext import ScrolledText
    
    def save_credentials():
        try:
            global id,pw,schedule
            id=input_id.get()
            pw=input_pw.get()
            schedule_array_text=str(st.get(1.0, END)).split("\n")
            schedule_array=[]
            for i in schedule_array_text:

                if i == "":
                    continue
                else:
                    if len(schedule_array) < 9:
                        schedule_array.append(i)
                    else:
                        messagebox.showwarning("스케줄 한도 초과", "스케줄은 부정사용 방지를 위해 최대 9개까지만 등록됩니다")
                        print(" 부정사용 방지를 위해 스케줄은 최대 9개까지만 등록됩니다.")
                    
            schedule=schedule_str_to_code(schedule_array)
            schedule_str=",".join(schedule_array)
#            schedule_str_to_code(schedule_array)
            with open(fullpath, 'w', encoding='ANSI') as config:
                json_data={
                    "ID":"%s"%id,
                    "PW":"%s"%pw,
                    "SCHEDULE":"%s"%schedule_str
                }
                json.dump(json_data, config, indent=4,ensure_ascii=False)
                
            messagebox.showinfo("저장 성공", "변경사항이 저장되었습니다. 설정창을 닫아주세요.")
#            print("\033[93m [ALERT]\033[0m 변경사항이 저장되었습니다.")
            generate_login_token()
        except ValueError:
            messagebox.showwarning("저장 실패","입력값 중 잘못된 형식이 있습니다")
#            print("\033[93m [ALERT]\033[0m 입력값 중 잘못된 형식이 있습니다")
        except IndexError:
            messagebox.showwarning("저장 실패","입력값 중 잘못된 형식이 있습니다")
#            print("\033[93m [ALERT]\033[0m 입력값 중 잘못된 형식이 있습니다")
        except Exception as e:
            messagebox.showwarning("저장 실패","설정값을 확인해주세요")
#            print(e)
#            print("\033[93m [ALERT]\033[0m 저장하는데 실패했습니다. 설정값을 확인해주세요")
            
    root = Tk()
    root.resizable=(0,0)
    root.title("SETTINGS")
    root.iconbitmap(r"C:\Users\SJJeon\Desktop\icon.ico")
    font=font.Font(size=15, weight="bold")
    center_window(root, 300, 300)
    label1=Label(root, text='ID:')
    label2=Label(root, text="PW:")
    label3=Label(root, text="예약 스케줄: (맨윗줄부터 순서대로 예약진행됨)")
    input_id=Entry(root,width=33,justify='center')
    input_id.insert(0,id)
    input_pw=Entry(root,width=33,justify='center',text="%s"%pw)
    input_pw.insert(0,pw)
    save_button=Button(root,text="변경사항 저장",height = 2,width=42,command=save_credentials)
    st = ScrolledText(root,width=34,height=10,padx=20, pady=20)
    
    for i in range(0,len(schedule),1):
        timecode_=int(schedule[i][0])
        seatcode_=str(schedule[i][1])
        text="%s %s번\n"%(timeCodeToString(convert_timecode(timecode_)),seatcode_)
        text=text.replace("주말 ","")
        text=text.replace("평일 ","")
        st.insert(INSERT,text)
    
    label1.place(x=16,y=9)
    label2.place(x=16,y=39)
    label3.place(x=16,y=69)
    input_id.place(x=45,y=10)
    input_pw.place(x=45,y=40)
    st.place(x=0,y=94)
    save_button.place(x=0,y=260)
    root.mainloop()    

def is_live():

     try:
         response = urllib.request.urlopen('https://haslibrary-landingpage.whtjeon.vercel.app/')
         html = response.read()
         soup = BeautifulSoup(html, "html.parser")

         for tag in soup.find_all("meta"):
             if tag.get("property", None) == "og:islive":
                 islive=tag.get("content", None)

         if islive == "yes":
             return True
            
         elif islive =="no":
             return False
        
         else:
             return False

     except: 
         remove()
         print("\n  \033[31m[ERROR]\033[0m Unable to fetch verification server data")
         print("          인터넷 연결을 확인하고 다시 시도해주십시오.\n")
         print("\033[93m----------------------------------------------------------------\033[0m")

def isweekend():

    global state
    weekno = datetime.today().weekday() 
    
    if weekno<5: 
        state="평일"
        return False
    else: 
        state="주말"
        return True


def library_request_validation(library_response):

    global status,success
    
    if "예약 되었습니다." in library_response:
        status = "(성공)"
        success = True

    elif "도서관 예약가능시간이 아닙니다" in library_response:
        status = "예약가능시간이 아닙니다"
        success = False

    elif "같은 타임에 이미 예약하신 좌석이 있습니다" in library_response:
        status = "같은 타임에 이미 예약하신 좌석이 있습니다"
        success = False

    elif "이미 예약된 좌석입니다" in library_response:
        status = "이미 예약된 좌석입니다"
        success = False

    elif "해당 좌석은 이용하실 수 없습니다" in library_response:
        status = "해당 좌석은 이용하실 수 없습니다"
        success = False

    elif "예약가능시간이 아닙니다" in library_response:
        status = "예약가능시간이 아닙니다"
        success = False

    elif "하루에 두타임만 예약이 가능합니다" in library_response:
        status = "하루에 두타임만 예약이 가능합니다"
        success = False
        
    elif isloginvalid == False:
        status = "로그인 정보가 잘못되었습니다"
        success = False

    else:
        success = False
        try:
            response_dict = literal_eval(library_response)
            library_response_=response_dict["msg"]
            library_response_=library_response_.replace('.',"")
            status = "%s"%library_response_
#        
#        except SyntaxError:
#            status="로그인 정보가 잘못되었습니다"

        except Exception as e:
            print(e)
            status = "Unknown Error"

    return status,success

def convert_seatcode(seatcode):

    global seatcode_isvalid, real_seatcode
    # generate_login_token()
    url="https://hi.hana.hs.kr/SYSTEM_Plan/Lib_System/Lib_System_Reservation/popSeat_Reservation.asp"
    params=urllib.parse.urlencode({"code":"001","t_code":"28","dis_num":"%s"%seatcode})
    params=params.encode('utf-8')
    request=urllib.request.Request(url, params)
    response=opener.open(request)
    response=str(response.read().decode('utf-8'))
    
    if "도서관 예약가능시간이 아닙니다" in response:
        seatcode_isvalid = True
        real_seatcode=1
        return real_seatcode
        
    else:
        try:
            search_temp=re.compile('<input type="hidden" name="s_code" value="(.+?)">')
            matchobj=search_temp.search(response).group()
            real_seatcode = int(re.findall('\d+', matchobj)[0])
            seatcode_isvalid = True
            return real_seatcode
        
        except AttributeError:
            seatcode_isvalid = False
        
        except: 
            seatcode_isvalid = True

    return seatcode_isvalid

def library_reservation (timecode,seatcode):
    global FAIL_COUNT, SUCCESS_COUNT

    real_seatcode = convert_seatcode (seatcode)
    timecode_str=timeCodeToString(convert_timecode(timecode))

    if seatcode_isvalid == True and isloginvalid == True:
        library_url="https://hi.hana.hs.kr/SYSTEM_Plan/Lib_System/Lib_System_Reservation/reservation_exec.asp"
        library_params=urllib.parse.urlencode({"code":"001", "s_code":real_seatcode,"t_code": convert_timecode(timecode)})
        library_params=library_params.encode('utf-8')
        library_request=urllib.request.Request(library_url, library_params)
        library_response=opener.open(library_request)
        library_response=str(library_response.read().decode('utf-8'))
        library_request_validation(library_response)
        
        if success == False:
            FAIL_COUNT=FAIL_COUNT+1
            print (boldify("\033[31m [FAIL]\033[0m \033[93m%s %s번\033[0m (%s)"%(timecode_str,seatcode,status)))

        elif success == True:
            SUCCESS_COUNT=SUCCESS_COUNT+1
            print (boldify("\033[32m [SUCCESS]\033[0m \033[93m%s %s번\033[0m"%(timecode_str,seatcode)))
            
    elif seatcode_isvalid == True and isloginvalid == False:
        FAIL_COUNT=FAIL_COUNT+1
        print (boldify("\033[31m [FAIL]\033[0m \033[93m%s %s번\033[0m (로그인 정보가 잘못되었습니다)"%(timecode_str,seatcode)))

    elif seatcode_isvalid == False and isloginvalid == True: 
        FAIL_COUNT=FAIL_COUNT+1
        print (boldify("\033[31m [FAIL]\033[0m \033[93m%s %s번\033[0m (잘못된 좌석번호입니다)"%(timecode_str,seatcode)))
        
    else:
        FAIL_COUNT=FAIL_COUNT+1
        print (boldify("\033[31m [FAIL]\033[0m \033[93m%s %s번\033[0m (잘못된 로그인 정보와 잘못된 좌석번호입니다)"%(timecode_str,seatcode)))

def library_reservation_auto (schedule):
    
    global SUCCESS_COUNT, FAIL_COUNT

    FAIL_COUNT=0
    SUCCESS_COUNT=0

    print("\n")
 
    for i in range(0,len(schedule),1):
        timecode=int(schedule[i][0])
        seatcode=str(schedule[i][1])
        library_reservation (timecode,seatcode)

    print ("\n Process Complete! (%s 성공, %s 실패)"%(SUCCESS_COUNT,FAIL_COUNT))
    print("\033[93m----------------------------------------------------------------\033[0m")

#from pyfiglet import Figlet
#f = Figlet(font='slant')
#print ("\033[93m%s\033[0m"%f.renderText('HAS LIBRARY'))

def timer():

    if isweekend()==False:
        target_time="13:00:00"
    else: 
        target_time="12:00:00"

    print(" [자동 예약] 예약시간이 되면 자동으로 좌석예약을 진행합니다.\n 아무것도 건들지 말고 가만히 기다려주세요.. (시계가 멈출수도..)\n")
    text_schedule_array=[]
    for i in range(0,len(schedule),1):
        timecode=int(schedule[i][0])
        seatcode=str(schedule[i][1])
        text_schedule="%s %s번"%(timeCodeToString(convert_timecode(timecode)),seatcode)
        text_schedule_array.append(text_schedule)

    print(" 자동 예약 스케줄: %s\n"%text_schedule_array)
    print(" 예약 시간: %s %s (%s)"%(today,target_time,state))
    
    while True:   
        now = datetime.now() + timedelta(seconds=1)
        print (" 현재 시간: "+now.strftime("%m/%d/%Y %H:%M:%S"), end="\r", flush=True)
        if now.strftime("%H:%M:%S") == target_time :
            remove()
            remove()
            print(" Here we go!\n")
            break
        time.sleep(1)
    
# Initalize Main Screen
remove()
print("\n                   COPYRIGHT ⓒ 2021 SJJEON ALL RIGHTS RESERVED.")
print("\033[93m+--------------------------------------------------------------+\033[0m")
print(boldify("\033[93m|          ** 하나고 도서관 간편 예약 스크립트 CLI **          |\033[0m"))
print("\033[93m+--------------------------------------------------------------+\033[0m")

check_config()
generate_login_token()

for step in track(range(100), description="Connecting"):
    time.sleep(0.005)
continue_option=1

def mainmenu():
    if username == "NULL":
        welcome_msg=" \033[31m로그인 정보 잘못됨\033[0m"
        
    else:        
        welcome_msg="    USER: %s님"%username
        
    print("  Status: \033[92mLIVE (Connected)\033[0m                  %s\n"%welcome_msg)
    print("  1. 도서관 예약하기 (자동)\n")
    print("  2. 도서관 예약하기 (수동)\n")
    print("  3. 학생 계정 정보 및 예약 스케줄 수정\n")
    print("  4. Refresh Login Token (로그인 오류 시 사용)\n")
    print("  5. 프로그램 오류 및 기능 건의\n")
    print("  0. 메인메뉴 화면으로 돌아가기\n")
    print("\033[93m----------------------------------------------------------------\033[0m")
    
if is_live():
    remove()
    mainmenu()
    
else:
    remove()
    print("  Status: \033[91mDEAD\033[0m\n")
    print("        현재 개발자에 의해 사용이 중단된 프로그램입니다\n")
    print("\033[93m----------------------------------------------------------------\033[0m")
    continue_option=2
    count_down = 30
    while (count_down):
        count_down -= 1
        print ("  %s초 후에 자동 종료됩니다."%count_down, end="\r", flush=True)
        if count_down != 0:
            time.sleep(1)
        
while continue_option==1:

    option = input(" Enter Choice and Press Enter: ")
    if option == "1":
        remove()
        continue_option = 1
        timer()
        # generate_login_token()
        library_reservation_auto(schedule)

    elif option == "2":
        # generate_login_token()
        print("\n [수동 예약] 예약할 타임과 좌석번호를 입력해주세요\n")
        timecode_input = int(input(" 타임: "))
        seatcode_input = int(input(" 좌석번호: "))
        print("")
        library_reservation(timecode_input,seatcode_input)
        print("\033[93m----------------------------------------------------------------\033[0m")

    elif option == "3":
        credentials()
        print ("\n 인트라넷 아이디: %s"%id)
        print (" 인트라넷 PW: %s"%pw)
        # temp_option = input("수정하시려면 1번, 메인화면으로 돌아가시려면 0번을 눌러주세요")
        # if temp_option == "1":
        print("\n 자동예약스케줄:")

        for i in range(0,len(schedule),1):
            timecode=int(schedule[i][0])
            seatcode=str(schedule[i][1])
            print(" %s. %s %s번"%(i+1,timeCodeToString(convert_timecode(timecode)),seatcode))
            
        print("\033[93m----------------------------------------------------------------\033[0m")

    elif option == "4":
        generate_login_token()
        print(" Successfully Refreshed Login Token!")
        print("\033[93m----------------------------------------------------------------\033[0m")

    elif option == "5":
        print("\n 익명 에스크에 자유롭게 의견을 남겨주시면\n 시간 날때 수정하거나 업데이트하겠습니다. (아마 안 할 예정..)")
        import webbrowser
        asked_url="https://asked.kr/haslibrary20"
        webbrowser.open(asked_url)
        print("\033[93m----------------------------------------------------------------\033[0m")

    elif option == "215":
        
        temp=input("Seatcode: ")
        convert_seatcode(temp)
        if seatcode_isvalid == True:
            print("Status: VAlID")
            print("S_Code: %s"%real_seatcode)
        elif seatcode_isvalid == False:
            print("Status: INVALID")

        print("\033[93m----------------------------------------------------------------\033[0m")

    elif option == "9":
        continue_option = 2
        print("Bye-Bye")
        
    elif option == "0":
        print("\033[93m----------------------------------------------------------------\033[0m")
        mainmenu()

    else:
        remove()
        print("\033[33m[Warning]\033[0m 1~6 사이 옵션을 선택하십시오 (숫자)")
        continue

    
    
    
