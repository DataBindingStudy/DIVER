# Directory description

![image](https://github.com/user-attachments/assets/e4817d1e-6d4e-417d-9eda-fda8b9187a22)



Source code description 

1. SringTest  
&emsp;src/main/java  
&emsp;&emsp;com.test.helloworld  
&emsp;&emsp;&emsp;BindingNode.java   ------  Node Definition of NPG  
&emsp;&emsp;&emsp;ListGraph.java  ------  The structure and basic operating Methods of NPG  
&emsp;&emsp;&emsp;MyMapUtil.java  ------  Major functional code  
&emsp;&emsp;&emsp;HelloController.java  ------  Web API interface   
&emsp;&emsp;org.springframework.beans  
&emsp;&emsp;&emsp;Spring_Instrumentation.java  ------  Definition of Instrumentation Class  
&emsp;&emsp;&emsp;others  ------  Overwrite some files in org.springframework.beans and add calls to instrumentation classes  

3. garilsMain   
&emsp;grails-app/controllers/garilsmain  
&emsp;&emsp;BindingNode.java  ------  Node Definition of NPG  
&emsp;&emsp;ListGraph.java  ------  The structure and basic operating Methods of NPG  
&emsp;&emsp;NewGetPropertyChain.groovy  ------  Major functional code  
&emsp;&emsp;XXXController.java  ------  Web API interface   



# Getting Started

Test environment:

​	OS: Ubuntu 20.04 LTS

​	Docker: Version 20.10.21

​	Python: Version 3.8.10



1. Download example folder

    

2. Build docker

    ```bash
    $ cd example/docker/
    $ ./docker_build.sh
    ```

    

3. Start web service
   
    ```bash
    $ cd ../fuzzing/DoS/
    $ ./restart_docker.sh
    ```
    
    
    
4. Obtain bindable nested properties

    4.1. Open the browser, input `http://127.0.0.1:8080/helloworld/FindwithBFS?depth=10`, and wait about ten minutes.

    4.2. Copy the result to the `nps.txt` file, and remove the first two lines.

    

5. Fuzzing to find DoS vulnerabilities, including OSDoS and WSDoS
   
    ```bash
    $ python3 fuzzing_DoS.py
    ```
    `DoS_result.txt` is the fuzzing result.
    
    ```bash
    WSDoS: {'class.module.classLoader.resources.context.path': ''}
    OSDoS: thread changed from 17 to 24: {'class.module.classLoader.resources.context.startStopThreads': '100'}
    WSDoS: {'class.module.classLoader.resources.context.catalinaBase.executable': 'false'}
    OSDoS: thread changed from 17 to 26: {'class.module.classLoader.resources.context.parent.startStopThreads': '100'}
    WSDoS: {'class.module.classLoader.resources.context.catalinaBase.parentFile.executable': 'false'}
    WSDoS: {'class.module.classLoader.resources.context.manager.engine.defaultHost': ''}
    OSDoS: thread changed from 17 to 24: {'class.module.classLoader.resources.context.manager.engine.startStopThreads': '100'}
    WSDoS: {'class.module.classLoader.resources.context.parent.appBaseFile.executable': 'false'}
    WSDoS: {'class.module.classLoader.resources.context.manager.engine.service.mapper.defaultHostName': ''}
    OSDoS: thread changed from 17 to 24: {'class.module.classLoader.resources.context.manager.engine.service.server.utilityThreads': '100'}
    WSDoS: {'class.module.classLoader.resources.context.parent.configBaseFile.parentFile.parentFile.executable': 'false'}
    ```
    
    `DoS_output.txt` is the details of the fuzzing process.
    
    
    
5. Fuzzing to find AFR vulnerabilities
   
    ```bash
    $ cp nps.txt ../AFR
    $ cd ../AFR
    $ ./restart_docker.sh
    $ python3 fuzzing_AFR.py
    ```
    `AFR_result.txt` is the fuzzing result.
    
    ```bash
    AFR: class.module.classLoader.resources.context.parent.appBase
    ```
    
    `AFR_output.txt` is the details of the fuzzing process.





# Detailed Description

1. Compile

    1.1 Spring

    ​	(1) Unzip SpringTest.zip and open it in IDEA

    ​	(2) Choose SDK:  File -> Project Structure ->Project

    ​	(3) Build package:  Build -> Build Artifacts

    ​	(4) Find "hello. war" in the "target" folder

    1.2 Grails

    ​	(1)  Unzip garilsMain.zip and open it in IDEA

    ​	(2) Choose SDK:  File -> Project Structure ->Project

    ​	(3) Modify build.gradle: If you want to compile the Tomcat version, overwrite build.gradle with the build.gradle_tomcat file; If you want to compile the Jetty version, overwrite build.gradle_jetty with the build.gradle_jetty file

    ​	(4) Compile a modified grails-databinding-5.2.0.jar：（!!! This step can be skipped as there are compiled packages in the grails core changed folder）

    ​		(a) Download grails-core-5.2.0 and cd grails-core-5.2.0/grails-databinding/src/main/groovy/grails/databinding

    ​		(b) Add Grails_Instrumentation.java  and  change  SimpleDataBinder.groovy  （the files is in garilsMain\grails-core-changed）

    ​		(c) cd grails-core-5.2.0;./gradlew install

    ​		(d) get the package in grails-core-5.2.0/grails-databinding/build/libs

    ​	(5) Find the location of the grails-databinding package in the IDEA project and replace it: 

    ​		External Libraries -> Gradle: org.grails:grails-databinding:5.2.0 ->Open Library Settings

    ​		You will find the actual addresses of two files and replace them ,for example: 
    ​         /root/.gradle/caches/modules-2/files-2.1/org.grails/grails-databinding/5.2.0/9d040e853f7cfc2d831be7a304e486a246f620b4/grails-databinding-5.2.0.jar
    ​         /root/.gradle/caches/modules-2/files-2.1/org.grails/grails-databinding/5.2.0/2f08da7b92c4a052b36f1abce228e0ac899d2753/grails-databinding-5.2.0-sources.jar

    ​	(6) Find "garilsMain-0.1-plain.war" in the "build/libs" folder

    

2. Build test environment

    2.1 Put the compiled war package in the corresponding directory, such as `example/docker`

    2.2 Build docker, refer to Getting Started. The Dockerfile of Gettting Started is for Tomcat, The Dockerfile for Jetty is as follows:

    ```dockerfile
    FROM ubuntu
    
    USER root
    RUN apt update
    RUN apt install openjdk-11-jdk -y
    
    RUN useradd -m -s /bin/bash jettyuser
    USER jettyuser
    WORKDIR /home/jettyuser
    COPY jetty-distribution-9.4.50.v20221201.tar.gz /home/jettyuser
    RUN tar -zxvf jetty-distribution-9.4.50.v20221201.tar.gz
    COPY helloworld.war jetty-distribution-9.4.50.v20221201/webapps
    
    EXPOSE 8080
    CMD ["/home/jettyuser/jetty-distribution-9.4.50.v20221201/bin/jetty.sh", "run"]
    ```

    

3. Fuzzing

    Refer to Getting Started.


