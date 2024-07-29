import requests
import time
import subprocess
import sys
import random
import os
from requests.exceptions import ReadTimeout


def random_int(value, up):
    a = random.randint(0, up)
    return str(a)


str_pattern = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r\x0b\x0c'


def generate_str(length=4):
    code1 = ''
    for _ in range(0, length):
        code1 = code1+str_pattern[random.randint(0, len(str_pattern)-1)]
    return code1


def replace_a_char(value):
    if (len(value) < 1):
        return ""
    index = random.randint(1, len(value))
    return value[:index-1]+generate_str(1)+value[index:]


def insert_str(value):
    index = random.randint(0, len(value))
    return value[:index]+generate_str(4)+value[index:]


def truncate_str(value):
    if (len(value) < 1):
        return ""
    end = random.randint(1, len(value))
    return value[:end]


int_dict = {
    'java.lang.Integer': ["100", "-1", "0", "9999999", "-2147483648", "2147483647", "99999999999", "-99999999999"],
    'int': ["1", "-1", "0", "99999", "-2147483648", "2147483647", "99999999999", "-99999999999"],
    'java.lang.Long': ["1", "-1", "0", "99999", "-9223372036854775808", "9223372036854775807", "9999999999999999999999", "-9999999999999999999999"],
    'long': ["1", "-1", "0", "99999", "-9223372036854775808", "9223372036854775807", "9999999999999999999999", "-9999999999999999999999"]
}


def Type_aware_Mutation(fkey, ftype, fvalue, fenum):
    fresult = [""]
    if ftype == "Enum_type":
        fenum.append("")
        return fenum
    elif ftype == 'java.lang.Boolean' or ftype == 'boolean':
        return ["", "true", "false"]
    elif ftype in int_dict.keys():
        fresult = int_dict[ftype][:]
        fresult.append(random_int(fvalue, 999))
        fresult.append(random_int(fvalue, 99999))
        return fresult
    elif "E1rr0r" in fvalue or len(fvalue) == 0:
        fresult.append(generate_str(5))
        fresult.append(generate_str(10))
        return fresult
    else:
        fresult.append(replace_a_char(fvalue))
        fresult.append(insert_str(fvalue))
        fresult.append(truncate_str(fvalue))
        return fresult


def get_thread_num(url):
    try:
        result = requests.get(url[:url.rfind("/")]+"/GetThread", timeout=10)
        if "200" != str(result.status_code):
            return -1
        else:
            return int(result.text)
    except Exception as e:
        print(e)
        return -1


def check_path(path):
    path2 = path.lower()
    if "thread" in path2:
        return 1
    if "executable" in path2:
        return 2
    return 0


def fuzz(fuzz_input_filename, fuzz_url, sleep_time, web_server, fuzz_result_filename):
    with open(fuzz_input_filename, "r") as f:
        for line in f.readlines():
            if len(line) > 0:
                fuzz_all = line.strip().split(" ")
                if len(fuzz_all) < 2:
                    continue
                elif len(fuzz_all) == 2:
                    fuzz_key = fuzz_all[0]
                    fuzz_type = fuzz_all[1]
                    fuzz_value = ""
                    fuzz_enum = []
                else:
                    fuzz_key = fuzz_all[0]
                    fuzz_type = fuzz_all[1]
                    fuzz_value = fuzz_all[2]
                    fuzz_enum = fuzz_all[3:]

                fuzz_value_list = Type_aware_Mutation(
                    fuzz_key, fuzz_type, fuzz_value, fuzz_enum)

                # fuzzing DoS
                fuzz_mode = check_path(fuzz_key)
                thread_num = 0
                if (fuzz_mode == 1):
                    thread_num = get_thread_num(fuzz_url)
                for fuzz_value in fuzz_value_list:
                    data = {fuzz_key: fuzz_value}
                    print(data)
                    try:
                        result = requests.get(fuzz_url, timeout=10)
                        status_code = result.status_code
                        print("---before fuzz status code---: ", status_code)
                        if "200" != str(status_code):
                            # writeExceptUrl("last np except: " + str(data), fuzz_result_filename)
                            restartServer(sleep_time, web_server)
                        result = requests.post(fuzz_url, data=data, timeout=10)
                        print("---fuzz status code---: ", result.status_code)
                        if (fuzz_mode == 1):
                            time.sleep(1)
                        elif (fuzz_mode == 2):
                            time.sleep(10)

                        try:
                            result = requests.get(fuzz_url, timeout=10)
                            status_code = result.status_code
                            print("---after fuzz status code---: ", status_code)
                            if "200" != str(status_code):
                                writeExceptUrl(
                                    "WSDoS: " + str(data), fuzz_result_filename)
                                restartServer(sleep_time, web_server)
                                break
                        except ConnectionError as e:
                            print(e)
                            writeExceptUrl("WSDoS: " + str(data) +
                                           "(ConnectionError)", fuzz_result_filename)
                            restartServer(sleep_time, web_server)
                            break
                        except ReadTimeout as e:
                            print(e)
                            writeExceptUrl("WSDoS: " + str(data) +
                                           "(TimeoutError)", fuzz_result_filename)
                            restartServer(sleep_time, web_server)
                            break
                        except Exception as e:
                            print(e)
                            writeExceptUrl(
                                "except: " + str(data) + ": " + str(e), fuzz_result_filename)
                            restartServer(sleep_time, web_server)
                            break

                        if (fuzz_mode == 1):
                            thread_num2 = get_thread_num(fuzz_url)
                            # writeExceptUrl("Thread changed from "+str(thread_num)+ " to "+str(thread_num2)+": " + str(data), web_server)
                            if thread_num < thread_num2:
                                writeExceptUrl("OSDoS: thread changed from "+str(thread_num) +
                                               " to "+str(thread_num2)+": " + str(data), fuzz_result_filename)
                                restartServer(sleep_time, web_server)
                                break

                    except Exception as e:
                        print(e)
                        writeExceptUrl("except: " + str(data) +
                                       ": " + str(e), fuzz_result_filename)
                        restartServer(sleep_time, web_server)
                        break


def restartServer(sleep_time, web_server):
    print(web_server+" restarted")
    child_server_process = subprocess.Popen(
        "./restart_docker.sh", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(sleep_time)


def writeExceptUrl(exdata, fuzz_result_filename):
    with open(fuzz_result_filename, "a", encoding="utf-8") as fa:
        fa.write(exdata+"\n")


def main():
    start = time.time()
    sleep_time = 20
    web_server = "tomcat"
    restartServer(sleep_time, web_server)
    sys.stdout = open('DoS_output.txt', 'w')
    fuzz_input_filename = "nps.txt"
    fuzz_result_filename = "DoS_result.txt"
    fuzz_url = "http://127.0.0.1:8080/helloworld/greeting"
    fuzz(fuzz_input_filename, fuzz_url, sleep_time,
         web_server, fuzz_result_filename)
    stop = time.time()
    print('Running time: %f Seconds' % (stop-start))
    sys.stdout.close()
    sys.stdout = sys.__stdout__


if __name__ == '__main__':
    main()
