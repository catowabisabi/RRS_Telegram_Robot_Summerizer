# 使用官方Python 3.10運行時作為父映像
FROM python:3.10-slim

# 設置工作目錄為/app
WORKDIR /app

# 將當前目錄內容複製到位於/app的容器中
COPY . /app

# 安裝requirements.txt中指定的所有需要的包
RUN pip install --no-cache-dir -r requirements.txt


# 使用CMD指令啟動你的bot
CMD ["python", "run.py"]