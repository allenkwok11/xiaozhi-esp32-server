#!/bin/bash

# 应用名称和JAR包路径
APP_NAME="xiaozhi-esp32-api"
JAR_FILE="xiaozhi-esp32-api.jar"
PID_FILE="xiaozhi-server.pid"
PROFILE="dev"

# 创建日志目录
LOG_DIR="logs"
mkdir -p $LOG_DIR

# 获取当前日期和时间作为日志文件名（精确到秒）
CURRENT_DATETIME=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/${APP_NAME}_${CURRENT_DATETIME}.log"

# 检查JAR文件是否存在，如果不存在则尝试在target目录中查找
if [ ! -f "$JAR_FILE" ]; then
    
    # 检查target目录是否存在
    if [ -d "target" ]; then
        # 在target目录中查找JAR文件
        TARGET_JAR=$(find target -name "$JAR_FILE" -type f | head -n 1)
        
        if [ -n "$TARGET_JAR" ]; then
            JAR_FILE="$TARGET_JAR"
        else
            # 如果找不到指定名称的JAR，尝试查找任何JAR文件
            TARGET_JAR=$(find target -name "*.jar" -not -name "*sources.jar" -not -name "*javadoc.jar" -not -name "*tests.jar" -type f | head -n 1)
            
            if [ -n "$TARGET_JAR" ]; then
                JAR_FILE="$TARGET_JAR"
            else
                echo "错误: 无法找到JAR文件，请确保已编译项目"
                exit 1
            fi
        fi
    else
        echo "错误: 未找到target目录，请确保已编译项目"
        exit 1
    fi
fi

# 检查是否已经有实例在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat $PID_FILE)
    if ps -p $OLD_PID > /dev/null; then
        echo "发现已运行的实例 (PID: $OLD_PID)，正在停止..."
        kill $OLD_PID
        sleep 5
        
        # 检查进程是否仍在运行，如果是则强制终止
        if ps -p $OLD_PID > /dev/null; then
            echo "进程未能正常终止，正在强制终止..."
            kill -9 $OLD_PID
            sleep 2
        fi
    fi
fi

# 启动应用
nohup java -jar $JAR_FILE --spring.profiles.active=$PROFILE > $LOG_FILE 2>&1 & echo $! > $PID_FILE
echo "$APP_NAME 已启动，PID: $(cat $PID_FILE)"

# 创建一个符号链接指向最新的日志文件，方便查看
LATEST_LOG_LINK="$LOG_DIR/${APP_NAME}_latest.log"
if [ -L "$LATEST_LOG_LINK" ]; then
    rm "$LATEST_LOG_LINK"
fi
ln -s "$(basename $LOG_FILE)" "$LATEST_LOG_LINK"
echo "最新日志文件链接: $LATEST_LOG_LINK"
