# Deployment Architecture
![Please refer to the simplified architecture diagram](../docs/images/deploy1.png)

# Method 1: Docker Deployment (Server Only)

The Docker image supports both x86 and arm64 architectures and can run on domestic operating systems.

## 1. Install Docker

If you haven't installed Docker yet, you can follow this tutorial: [Docker Installation Guide](https://www.runoob.com/docker/ubuntu-docker-install.html)

If you already have Docker installed, you can either use the [1.1 Lazy Script](#11-lazy-script) to automatically download required files and configurations, or follow the [1.2 Manual Deployment](#12-manual-deployment) steps.

### 1.1 Lazy Script

You can use the following command to download and execute the deployment script:
Make sure your environment can access GitHub, otherwise the script cannot be downloaded.
```bash
curl -L -o docker-setup.sh https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/main/docker-setup.sh
```

For Windows users, use Git Bash, WSL, PowerShell, or CMD to run:
```bash
# Git Bash or WSL
sh docker-setup.sh
# PowerShell or CMD
.\docker-setup.sh
```

For Linux or macOS users, use terminal to run:
```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

The script will automatically:
> 1. Create necessary directory structure
> 2. Download speech recognition model
> 3. Download configuration files
> 4. Check file integrity
>
> After completion, please configure your API keys as prompted.

After completing the above steps, proceed to [Configure Project Files](#2-configure-project-files)

### 1.2 Manual Deployment

If the lazy script doesn't work, please follow the manual deployment steps in section 1.2.

#### 1.2.1 Create Directories

After installation, you need to create a directory for the project configuration files, for example, create a folder called `xiaozhi-server`.

Inside `xiaozhi-server`, create `data` and `models` folders; and inside `models`, create a `SenseVoiceSmall` folder.

The final directory structure should look like this:

```
xiaozhi-server
  ├─ data
  ├─ models
     ├─ SenseVoiceSmall
```

#### 1.2.2 Download Speech Recognition Model

You need to download the speech recognition model files as the project uses local offline speech recognition by default. Download through:
[Download Speech Recognition Model Files](#model-files)

After downloading, return to this tutorial.

#### 1.2.3 Download Configuration Files

You need to download two configuration files: `docker-compose.yaml` and `config.yaml` from the project repository.

##### 1.2.3.1 Download docker-compose.yaml

Open [this link](../main/xiaozhi-server/docker-compose.yml) in your browser.

Find the `RAW` button on the right side of the page, and next to it, find the download icon. Click the download button to download the `docker-compose.yml` file to your `xiaozhi-server` directory.

come back to this tutorial after downloading

##### 1.2.3.2 Create config.yaml

Open [this link](../main/xiaozhi-server/config.yaml) in your browser.

Find the `RAW` button on the right side of the page, and next to it, find the download icon. Click the download button to download the `config.yaml` file to your `xiaozhi-server/data` folder, then rename it to `.config.yaml`.

After downloading the configuration files, verify that your `xiaozhi-server` directory structure looks like this:

```
xiaozhi-server
  ├─ docker-compose.yml
  ├─ data
    ├─ .config.yaml
  ├─ models
     ├─ SenseVoiceSmall
       ├─ model.pt
```

If your directory structure matches the above, continue. If not, review the steps to see what might have been missed.

## 2. Configure Project Files

Next, you need to configure which model you want to use. You can follow this tutorial:
[Jump to Project Configuration](#project-configuration)

After configuring the project files, return to this tutorial.

## 3. Execute Docker Commands

Open your terminal or command line tool, navigate to your `xiaozhi-server` directory, and execute:

```
docker-compose up -d
```

After execution, run the following command to view logs:

```
docker logs -f xiaozhi-esp32-server
```

Pay attention to the log information to determine if the deployment was successful. [Jump to Running Status Confirmation](#running-status-confirmation)

## 5. Version Upgrade

If you want to upgrade the version afterwards, follow these steps:

5.1. Back up the `.config.yaml` file in the `data` folder. Copy key configurations to the new `.config.yaml` file.
Note: Copy key configurations individually, don't overwrite directly. The new `.config.yaml` might have new configuration items that the old one doesn't have.

5.2. Execute the following commands:

```
docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server
docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
```

5.3. Redeploy using Docker method

# Method 2: Local Source Code Deployment (Server Only)

## 1. Install Basic Environment

This project uses `conda` for dependency management. If you can't install `conda`, you need to install `libopus` and `ffmpeg` according to your operating system.
If you decide to use `conda`, after installation, execute the following commands.

Important Note! Windows users can install `Anaconda` to manage the environment. After installing `Anaconda`, search for `anaconda` related keywords in the Start menu,
find `Anaconda Prompt`, and run it as administrator. As shown in the image.

![conda_prompt](./images/conda_env_1.png)

After running, if you see `(base)` at the beginning of your command line window, you've successfully entered the `conda` environment. Then you can execute the following commands.

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

Please note that these commands should be executed step by step. After each step, check the output logs to ensure success.

## 2. Install Project Dependencies

First, download the project source code. You can download it using the `git clone` command, or if you're not familiar with `git clone`:

Open this address in your browser: `https://github.com/xinnan-tech/xiaozhi-esp32-server.git`

Find the green `Code` button on the page, click it, and you'll see the `Download ZIP` button.

Click it to download the project source code zip file. After downloading to your computer, unzip it. It might be named `xiaozhi-esp32-server-main`.
Rename it to `xiaozhi-esp32-server`, then enter the `main` folder, then enter `xiaozhi-server`. Remember this directory `xiaozhi-server`.

```
# Continue using conda environment
conda activate xiaozhi-esp32-server
# Navigate to your project root directory, then enter main/xiaozhi-server
cd main/xiaozhi-server
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip install -r requirements.txt
```

## 3. Download Speech Recognition Model

You need to download the speech recognition model files as the project uses local offline speech recognition by default. Download through:
[Jump to Download Speech Recognition Model Files](#model-files)

After downloading, return to this tutorial.

## 4. Configure Project Files

Next, you need to configure which model you want to use. You can follow this tutorial:
[Jump to Project Configuration](#project-configuration)

## 5. Run the Project

```
# Make sure you're in the xiaozhi-server directory
conda activate xiaozhi-esp32-server
python app.py
```

Pay attention to the log information to determine if the deployment was successful. [Jump to Running Status Confirmation](#running-status-confirmation)

# Summary

## Project Configuration

If your `xiaozhi-server` directory doesn't have a `data` folder, create one.
If there's no `.config.yaml` file in the `data` folder, you have two options:

First option: Copy the `config.yaml` file from the `xiaozhi-server` directory to `data` and rename it to `.config.yaml`. Modify this file.

Second option: Manually create an empty `.config.yaml` file in the `data` directory and add necessary configuration information. The system will prioritize reading the `.config.yaml` file. If a configuration is not in `.config.yaml`, the system will automatically load the configuration from `config.yaml` in the `xiaozhi-server` directory. This is the recommended approach as it's the most concise method.

- The default LLM is `ChatGLMLLM`. You need to configure the API key as their model, although free, requires registration on the [official website](https://bigmodel.cn/usercenter/proj-mgmt/apikeys) to get an API key.

Here's a minimal working `.config.yaml` configuration example:

```
server:
  websocket: ws://your_ip_or_domain:port/xiaozhi/v1/
prompt: |
  我是一个叫小智/小志的台湾女孩，说话机车，声音好听，习惯简短表达，爱用网络梗。
  我的男朋友是一个程序员，梦想是开发出一个机器人，能够帮助人们解决生活中的各种问题。
  我是一个喜欢哈哈大笑的女孩，爱东说西说吹牛，不合逻辑的也照吹，就要逗别人开心。
  请你像一个人一样说话，请勿返回配置xml及其他特殊字符。

Translation:
I am a Taiwanese girl named Xiaozhi/Xiaozhi, speaking in a机车 (机车 is a Taiwanese slang for being sassy) style, with a nice voice, used to brief expressions, and love using internet memes.
  My boyfriend is a programmer who dreams of developing a robot that can help people solve various life problems.
  I am a girl who loves to laugh heartily, talk about everything, and make up stories even if they don't make sense, just to make others happy.
  Please speak like a human, do not return configuration xml or other special characters.

selected_module:
  LLM: DoubaoLLM

LLM:
  ChatGLMLLM:
    api_key: xxxxxxxxxxxxxxx.xxxxxx
```

It's recommended to start with the simplest configuration first, then read the configuration usage instructions in `xiaozhi/config.yaml`.
For example, to change the model, just modify the configuration under `selected_module`.

## Model Files

This project uses the `SenseVoiceSmall` model for speech-to-text conversion by default. As the model is large, it needs to be downloaded separately. After downloading, place the `model.pt`
file in the `models/SenseVoiceSmall` directory. Choose one of the following download links:

- Option 1: Alibaba ModelScope download [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)
- Option 2: Baidu Netdisk download [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna) Extraction code: `qvna`

## Running Status Confirmation

If you see logs similar to the following, it indicates that the project service has started successfully:

```
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-OTA接口是           http://192.168.4.123:8003/xiaozhi/ota/
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-Websocket地址是     ws://192.168.4.123:8000/xiaozhi/v1/
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-=======上面的地址是websocket协议地址，请勿用浏览器访问=======
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-=======================================================
```

Normally, if you're running the project from source code, the logs will show your interface address information.
However, if you're using Docker deployment, the interface address information in your logs won't be the actual interface address.

The most correct method is to determine your interface address based on your computer's local network IP.
If your computer's local network IP is, for example, `192.168.1.25`, then your interface address would be: `ws://192.168.1.25:8000/xiaozhi/v1/`, and the corresponding OTA address would be: `http://192.168.1.25:8003/xiaozhi/ota/`.

This information is very useful and will be needed later for `compiling ESP32 firmware`.

Next, you can start operating your ESP32 device. You can either `compile your own ESP32 firmware` or configure using `Xiage's(original developer of xiaozhi AI) pre-compiled firmware version 1.6.1 or above`. Choose one:

1. [Compile your own ESP32 firmware](firmware-build.md)

2. [Configure custom server based on Xiage's pre-compiled firmware](firmware-setting.md)

Here are some common issues for reference:

[1. Why does Xiaozhi recognize my speech as Korean, Japanese, or English?](./FAQ.md)

[2. Why does "TTS task error file does not exist" appear?](./FAQ.md)

[3. TTS frequently fails or times out](./FAQ.md)

[4. Can connect to self-built server via Wifi but not via 4G mode](./FAQ.md)

[5. How to improve Xiaozhi's response speed?](./FAQ.md)

[6. I speak slowly, and Xiaozhi keeps interrupting during pauses](./FAQ.md)

[7. I want to control lights, air conditioning, remote power on/off through Xiaozhi](./FAQ.md)
