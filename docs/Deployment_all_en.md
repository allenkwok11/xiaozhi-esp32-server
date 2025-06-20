# Deployment Architecture 
![Please refer to the full module deployment architecture diagram](../docs/images/deploy2.png)

# Method 1: Docker Deployment (All Modules)

The Docker image supports both x86 and arm64 architectures and can run on domestic operating systems.

## 1. Install docker

If you haven't installed Docker, follow this guide: [Docker Installation](https://www.runoob.com/docker/ubuntu-docker-install.html)

#### 1.1 Create Project Directories

After installing Docker, you need to create a directory for the project configuration files, for example, create a folder named `xiaozhi-server`.

After creating the directory, you need to create a `data` folder and a `models` folder inside `xiaozhi-server`, and then create a `SenseVoiceSmall` folder inside `models`.

The final directory structure should look like this:

```
xiaozhi-server
  ├─ data
  ├─ models
     ├─ SenseVoiceSmall
```

#### 1.2.2 Download Speech Recognition Model
This project uses the `SenseVoiceSmall` model for speech-to-text conversion by default. As the model is large, it needs to be downloaded separately. After downloading, place the `model.pt` file in the `models/SenseVoiceSmall` directory. Choose one of the following download links:

- Option 1: Download from ModelScope (Aliyun) [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)

- Option 2: Download from Baidu Netdisk [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna) 
code: `qvna`

#### 1.3 Download Configuration Files
You need to download two configuration files: `docker-compose_all.yaml` and `config_from_api.yaml` from the project repository.

##### 1.3.1 Download docker-compose_all.yaml
Open [this link](../main/xiaozhi-server/docker-compose_all.yml) in your browser.

On the right side of the page, find the `RAW` button, and next to it, the download icon. Click the download button to download `docker-compose_all.yml` to your
`xiaozhi-server` directory.

Or directly run `wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/docker-compose_all.yml` to download.

After downloading, return to this tutorial and continue.

##### 1.3.2 Download config_from_api.yaml
Open [this link](../main/xiaozhi-server/config_from_api.yaml) in your browser.

On the right side of the page, find the `RAW` button, and next to it, the download icon. Click the download button to download `config_from_api.yaml` to your `data` folder inside `xiaozhi-server`, then rename `config_from_api.yaml` to `.config.yaml`.

Or directly run `wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/config_from_api.yaml` to download and save.

After downloading the configuration files, confirm that your `xiaozhi-server` directory looks like this:
```
xiaozhi-server
  ├─ docker-compose_all.yml
  ├─ data
    ├─ .config.yaml
  ├─ models
     ├─ SenseVoiceSmall
       ├─ model.pt
```

If your directory structure matches the above, continue. If not, check carefully to see if you missed any steps.

## 2. Data Backup
If you have previously run the management console and it contains your key information, please back up important data from the console first. The upgrade process may overwrite existing data.

## 3. Clean Up Old Docker Images and Containers
Next, open your terminal or command line tool, navigate to your `xiaozhi-server` directory, and execute the following commands:

```
docker compose -f docker-compose_all.yml down

docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server

docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web

docker stop xiaozhi-esp32-server-db
docker rm xiaozhi-esp32-server-db

docker stop xiaozhi-esp32-server-redis
docker rm xiaozhi-esp32-server-redis

docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
```

## 4. Start the New Containers
Run the following command to start the new version containers:

```
docker compose -f docker-compose_all.yml up -d
```

After execution, run the following command to check the logs:

```
docker logs -f xiaozhi-esp32-server-web
```

When you see output logs, it means your management console has started successfully.

```
2025-xx-xx 22:11:12.445 [main] INFO  c.a.d.s.b.a.DruidDataSourceAutoConfigure - Init DruidDataSource
2025-xx-xx 21:28:53.873 [main] INFO  xiaozhi.AdminApplication - Started AdminApplication in 16.057 seconds (process running for 17.941)
http://localhost:8002/xiaozhi/doc.html
```

Note: At this point, only the management console is running. If the `xiaozhi-esp32-server` on port 8000 reports an error, you can ignore it for now.

At this point, you need to use your browser to open the management console at http://127.0.0.1:8002 and register the first user. The first user will be the super administrator; all subsequent users will be regular users. Regular users can only bind devices and configure agents, while the super administrator can manage models, users, and parameters.

Next, you need to do three important things:

### The First Important Thing

Log in to the management console with the super administrator account, find "Parameter Management" in the top menu, locate the first entry in the list with the parameter code `server.secret`, and copy its value.


A note about `server.secret`: this value is very important as it allows the Server to connect to the manager-api. `server.secret` is a randomly generated key created each time the manager module is deployed from scratch.

After copying the parameter value, open the `.config.yaml` file in the `data` directory under `xiaozhi-server`. Your configuration file should look like this:

```
manager-api:
  url:  http://127.0.0.1:8002/xiaozhi
  secret: your_server.secret_value
```

1. Copy the `server.secret` value you just copied from the management console into the `secret` field in `.config.yaml`.

2. Since you are using Docker deployment, change the `url` to `http://xiaozhi-esp32-server-web:8002/xiaozhi`.

It should look like this:

```
manager-api:
  url: http://xiaozhi-esp32-server-web:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

After saving, proceed to the second important thing.

### The Second Important Thing

Log in to the management console with the super administrator account, go to "Model Configuration" in the top menu, then click "Large Language Model" in the left sidebar, find the first entry "Zhipu AI", and click the "Edit" button.

In the pop-up edit box, enter the API key you registered for Zhipu AI into the "API Key" field, then click save.

## 5. Restart xiaozhi-esp32-server

Next, open your terminal or command line tool and enter:

```
docker restart xiaozhi-esp32-server
docker logs -f xiaozhi-esp32-server
```

If you see logs similar to the following, it means the Server has started successfully.

```
25-02-23 12:01:09[core.websocket_server] - INFO - Websocket地址是      ws://xxx.xx.xx.xx:8000/xiaozhi/v1/
25-02-23 12:01:09[core.websocket_server] - INFO - =======上面的地址是websocket协议地址，请勿用浏览器访问=======
25-02-23 12:01:09[core.websocket_server] - INFO - 如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
25-02-23 12:01:09[core.websocket_server] - INFO - =======================================================
```
Since you are deploying all modules, you have two important interfaces to write into the ESP32 device.

OTA interface:
```
http://your_local_ip:8002/xiaozhi/ota/
```

WebSocket interface:
```
ws://your_local_ip:8000/xiaozhi/v1/
```

### The Third Important Thing


Log in to the management console with the super administrator account, go to "Parameter Management" in the top menu, find the parameter code `server.websocket`, and enter your WebSocket interface.

Log in to the management console with the super administrator account, go to "Parameter Management" in the top menu, find the parameter code `server.ota`, and enter your OTA interface.

Now you can start working with your ESP32 device. You can either compile your own ESP32 firmware or configure it using the pre-built firmware version 1.6.1 or above. Choose either option.


1. [Compile your own ESP32 firmware](firmware-build.md)
。
2. [Configure custom server based on pre-built firmware](firmware-setting.md)


# Method 2: Full Module Deployment from Source

## 1. Install MySQL Database
。
If MySQL is already installed on your machine, you can directly create a database named `xiaozhi_esp32_server`.

```sql
CREATE DATABASE xiaozhi_esp32_server CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

If you don't have MySQL, you can install it using Docker:

```
docker run --name xiaozhi-esp32-server-db -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 -e MYSQL_DATABASE=xiaozhi_esp32_server -e MYSQL_INITDB_ARGS="--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci" -e TZ=Asia/Shanghai -d mysql:latest
```

## 2. Install Redis

If you don't have Redis, you can install it using Docker:

```
docker run --name xiaozhi-esp32-server-redis -d -p 6379:6379 redis
```

## 3. Run manager-api Program

3.1 Install JDK21 and set the JDK environment variable

3.2 Install Maven and set the Maven environment variable

3.3 Use VSCode and install the necessary Java plugins

3.4 Use VSCode to load the manager-api module

Configure the database connection in `src/main/resources/application-dev.yml`:

```
spring:
  datasource:
    username: root
    password: 123456
```

Configure the Redis connection in `src/main/resources/application-dev.yml`:
```
spring:
    data:
      redis:
        host: localhost
        port: 6379
        password:
        database: 0
```

3.5 Run the main program

This project is a SpringBoot project. To start it:

Open `Application.java` and run the `Main` method to start

```
directory:
src/main/java/xiaozhi/AdminApplication.java
```

When you see output logs, it means your `manager-api` has started successfully.

```
2025-xx-xx 22:11:12.445 [main] INFO  c.a.d.s.b.a.DruidDataSourceAutoConfigure - Init DruidDataSource
2025-xx-xx 21:28:53.873 [main] INFO  xiaozhi.AdminApplication - Started AdminApplication in 16.057 seconds (process running for 17.941)
http://localhost:8002/xiaozhi/doc.html
```

## 4. Run manager-web Program

4.1 Install Node.js

4.2 Use VSCode to load the manager-web module

In the terminal, navigate to the manager-web directory:

```
npm install
```
Then start it:
```
npm run serve
```


Note: If your manager-api interface is not at `http://localhost:8002`, modify the path in `main/manager-web/.env.development` during development.


After running successfully, use your browser to open the management console at http://127.0.0.1:8001 and register the first user. The first user is the super administrator; subsequent users are regular users. Regular users can only bind devices and configure agents; the super administrator can manage models, users, and parameters.

Important: After registration, log in with the super administrator account, go to "Model Configuration" in the top menu, then click "Large Language Model" in the left sidebar, find the first entry "Zhipu AI", and click the "Edit" button.

In the pop-up edit box, enter the API key you registered for Zhipu AI into the "API Key" field, then click save.

## 5. Install Python Environment
This project uses `conda` to manage dependencies. If you can't install `conda`, you need to install `libopus` and `ffmpeg` according to your operating system.

If you use `conda`, after installation, execute the following commands:

Important: Windows users can install `Anaconda` to manage the environment. After installing `Anaconda`, search for `anaconda` in the Start menu,

find `Anaconda Prompt` and run it as administrator. See the image below.

![conda_prompt](./images/conda_env_1.png)

After running, if you see `(base)` at the beginning of the command line, you have successfully entered the `conda` environment. Now you can execute the following commands.

![conda_env](./images/conda_env_2.png)

```
conda remove -n xiaozhi-esp32-server --all -y
conda create -n xiaozhi-esp32-server python=3.10 -y
conda activate xiaozhi-esp32-server

# Add Tsinghua mirror channels
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge

conda install libopus -y
conda install ffmpeg -y
```

Note: Do not run all the commands at once. Execute them step by step, and after each step, check the output logs to ensure success.

## 6. Install Project Dependencies

First, download the project source code. You can use the `git clone` command, or if you are not familiar with it:

You can open this address in your browser: `https://github.com/xinnan-tech/xiaozhi-esp32-server.git`

After opening it, find the green `Code` button, click it, and then you will see the `Download ZIP` button.

Click it to download the project source code as a zip file. After downloading, extract it. The folder may be named `xiaozhi-esp32-server-main`.

You need to rename it to `xiaozhi-esp32-server`, then go into the `main` folder, then into `xiaozhi-server`. Remember this directory: `xiaozhi-server`.

```

# Continue using conda environment
conda activate xiaozhi-esp32-server

# Go to your project root directory, then enter main/xiaozhi-server
cd main/xiaozhi-server
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip install -r requirements.txt
```

### 7. Download Speech Recognition Model
The default speech-to-text model for this project is `SenseVoiceSmall`. Because the model is large, it needs to be downloaded separately. After downloading, place `model.pt` file into `models/SenseVoiceSmall` directory. You can choose either of the following download links:

- Option 1: Download from ModelScope (Aliyun) [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)
- Option 2: Download from Baidu Netdisk [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna) 
code: `qvna`

## 8. Configure Project Files
Log in to the management console with the super administrator account, go to "Parameter Management" in the top menu, find the first entry in the list with the parameter code `server.secret`, and copy its value.

A note about `server.secret`: this value is very important as it allows the Server to connect to the manager-api. `server.secret` is a randomly generated key created each time the manager module is deployed from scratch.

If your `xiaozhi-server` directory does not have a `data` folder, you need to create one.

If there is no `.config.yaml` file in `data`, you can copy `config_from_api.yaml` from the `xiaozhi-server` directory to `data` and rename it to `.config.yaml`.

After copying the parameter value, open the `.config.yaml` file in the `data` directory under `xiaozhi-server`. Your configuration file should look like this:

```
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: your_server.secret_value
```

Copy the `server.secret` value you just copied from the management console into the `secret` field in `.config.yaml`.

It should look like this:

```
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

## 9. Run the Project

```
# Make sure you are in the xiaozhi-server directory
conda activate xiaozhi-esp32-server
python app.py
```

If you see logs similar to the following, it means the project service has started successfully.

```
25-02-23 12:01:09[core.websocket_server] - INFO - Server is running at ws://xxx.xx.xx.xx:8000/xiaozhi/v1/
25-02-23 12:01:09[core.websocket_server] - INFO - =======上面的地址是websocket协议地址，请勿用浏览器访问=======
25-02-23 12:01:09[core.websocket_server] - INFO - 如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
25-02-23 12:01:09[core.websocket_server] - INFO - =======================================================
```

Since you are deploying all modules, you have two important interfaces.

OTA interface:
```
http://your_local_ip:8002/xiaozhi/ota/
```

WebSocket接口：
WebSocket interface:
```
ws://your_local_ip:8000/xiaozhi/v1/
```

Be sure to enter the above two interface addresses into the management console; they will affect the WebSocket address distribution and auto-upgrade functionality.

1. Log in to the management console with the super administrator account, go to "Parameter Management" in the top menu, find the parameter code `server.websocket`, and enter your WebSocket interface.

2. Log in to the management console with the super administrator account, go to "Parameter Management" in the top menu, find the parameter code `server.ota`, and enter your OTA interface.

Now you can start working with your ESP32 device. You can either compile your own ESP32 firmware or configure it using the pre-built firmware version 1.6.1 or above. Choose either option.

1. [Compile your own ESP32 firmware](firmware-build.md)

2. [Configure custom server based on pre-built firmware](firmware-setting.md)

# Frequently Asked Questions (FAQ)
Below are some common questions for your reference:

[1. Why does Xiaozhi recognize my speech as Korean, Japanese, or English?](./FAQ.md)

[2. Why does "TTS task error file does not exist" appear?](./FAQ.md)

[3. TTS frequently fails or times out](./FAQ.md)

[4. Can connect to self-built server via Wifi but not via 4G mode](./FAQ.md)

[5. How to improve Xiaozhi's response speed?](./FAQ.md)

[6. I speak slowly, and Xiaozhi keeps interrupting during pauses](./FAQ.md)

[7. I want to control lights, air conditioning, remote power on/off through Xiaozhi](./FAQ.md)
