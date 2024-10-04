# 使用官方 Python 運行時作為父映像
FROM python:3.12-slim

# 設置工作目錄
WORKDIR /app

# 將當前目錄內容複製到容器中的 /app
COPY . /app

# 安裝所需的套件
RUN pip install --no-cache-dir flask pgpt_python

# 設定環境變量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 暴露端口 5111
EXPOSE 5111

# 運行應用
CMD ["flask", "run", "--port=5111"]