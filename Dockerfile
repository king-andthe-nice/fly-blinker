# 使用官方 Python 轻量级镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制程序代码
COPY main.py .

# 启动程序
CMD ["python", "main.py"]
