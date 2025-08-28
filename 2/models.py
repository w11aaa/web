from settings import db


# house_info表的模型类
class House(db.Model):
    # 指定表名
    __tablename__ = 'house_info'
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    # 房源标题
    title = db.Column(db.String(100))
    # 房源户型
    rooms = db.Column(db.String(100))
    # 房源面积
    area = db.Column(db.String(100))
    # 房源价格
    price = db.Column(db.String(100))
    # 房源朝向
    direction = db.Column(db.String(100))
    # 租住类型
    rent_type = db.Column(db.String(100))
    # 房源所在区
    region = db.Column(db.String(100))
    # 房源所在街道
    block = db.Column(db.String(100))
    # 房源所在小区
    address = db.Column(db.String(100))
    # 交通条件
    traffic = db.Column(db.String(100))
    # 发布时间
    publish_time = db.Column(db.Integer)
    # 配套设施
    facilities = db.Column(db.TEXT)
    # 房屋优势
    highlights = db.Column(db.TEXT)
    # 周边
    matching = db.Column(db.TEXT)
    # 公交出行
    travel = db.Column(db.TEXT)
    # 浏览量
    page_views = db.Column(db.Integer)
    # 房东姓名
    landlord = db.Column(db.String(100))
    # 房东电话
    phone_num = db.Column(db.String(100))
    # 房源编号
    house_num = db.Column(db.String(100))

    # 重写__repr__方法，方便查看对象的输出内容
    def __repr__(self):
        return 'House: %s, %s' % (self.address, self.id)

# house_recommend表的模型类
# 用来存储用户的浏览记录
class Recommend(db.Model):
    # 指定表名
    __tablename__ = 'house_recommend'
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    # 用户ID
    user_id = db.Column(db.Integer)
    # 房源ID
    house_id = db.Column(db.Integer)
    # 房源标题
    title = db.Column(db.String(100))
    # 房源所在小区
    address = db.Column(db.String(100))
    # 房源所在街道
    block = db.Column(db.String(100))
    # 浏览次数
    score = db.Column(db.Integer)


# user_info表的模型类
# 用来存储用户的个人信息
class User(db.Model):
    # 指定表名
    __tablename__ = 'user_info'
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    # 用户昵称
    name = db.Column(db.String(100))
    # 用户密码
    password = db.Column(db.String(100))
    # 邮箱地址
    email = db.Column(db.String(100))
    # 用户住址
    addr = db.Column(db.String(100))
    # 用户收藏的房源编号
    collect_id = db.Column(db.String(250))
    # 用户浏览记录
    seen_id = db.Column(db.String(250))

    # 重写__repr__方法，方便查看对象的输出内容
    def __repr__(self):
        return 'User: %s, %s' % (self.name, self.id)