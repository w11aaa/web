# settings.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 获取项目当前路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 初始化Flask应用
app = Flask(__name__)

# --- 基本配置 ---
# 配置MySQL数据库连接
# 格式: 'mysql+pymysql://<用户名>:<密码>@<主机地址>:<端口>/<数据库名>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1:3306/house'
# 关闭自动跟踪修改，以提高性能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 设置用于Session加密的密钥，请在生产环境中更换为更复杂的值
app.config['SECRET_KEY'] = 'your-very-secret-key'

# 初始化SQLAlchemy，创建db对象
db = SQLAlchemy(app)