from flask import request, jsonify, redirect, url_for, session, Blueprint
from settings import app, db
from models import User, House
from sqlalchemy import or_

# 1. 从页面路由文件中导入 'pages' 蓝图
from index_page import pages

# 2. 创建一个名为 'api' 的新蓝图，用于处理所有后端数据接口
api = Blueprint('api', __name__)


# --- 辅助函数 ---
def house_to_dict(house):
    """将House对象转换为可序列化为JSON的字典"""
    return {
        'id': house.id,
        'title': house.title or f"{house.address} {house.rooms}",  # 确保title不为空
        'region': house.region,
        'block': house.block,
        'address': house.address,
        'rooms': house.rooms,
        'price': house.price,
        'page_views': house.page_views
    }


# --- 3. 定义 'api' 蓝图的所有路由 ---

# --- 搜索功能API (已升级) ---
@api.route('/search/recommendations')
def search_recommendations():
    """获取热门推荐房源（用于点击搜索框时显示）"""
    hot_houses = House.query.order_by(House.page_views.desc()).limit(10).all()
    houses_dict = [house_to_dict(h) for h in hot_houses]
    return jsonify(code=1, data=houses_dict)


@api.route('/search/keyword/', methods=['POST'])
def search_keyword():
    """根据关键词实时搜索房源"""
    keyword = request.form.get('kw', '')
    info_type = request.form.get('info', '')  # '地区搜索' 或 '户型搜索'

    if not keyword:
        return jsonify(code=0, msg='关键词为空')

    query = House.query
    search_term = f'%{keyword}%'
    if '地区' in info_type:
        query = query.filter(or_(
            House.region.like(search_term),
            House.block.like(search_term),
            House.address.like(search_term)
        ))
    elif '户型' in info_type:
        query = query.filter(House.rooms.like(search_term))

    results = query.limit(10).all()
    houses_dict = [house_to_dict(h) for h in results]

    if not houses_dict:
        return jsonify(code=0, msg=f'未找到关于 "{keyword}" 的房屋信息！')

    return jsonify(code=1, data=houses_dict)


# --- 用户认证API ---
@api.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(name=username, password=password).first()
    if user:
        session['user_id'] = user.id
        session['user_name'] = user.name
    return redirect(url_for('pages.index'))


@api.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    if User.query.filter_by(name=username).first():
        return redirect(url_for('pages.index'))
    new_user = User(name=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.id
    session['user_name'] = new_user.name
    return redirect(url_for('pages.index'))


@api.route('/logout')
def logout():
    session.clear()
    return jsonify(valid='1', msg='已退出登录')


# --- 用户操作API ---
@api.route('/add/collection/<int:house_id>')
def add_collection(house_id):
    if 'user_id' not in session:
        return jsonify(valid='0', msg='请先登录！')
    user = User.query.get(session['user_id'])
    collect_ids = user.collect_id.split(',') if user.collect_id else []
    if str(house_id) not in collect_ids:
        collect_ids.append(str(house_id))
        user.collect_id = ','.join(filter(None, collect_ids))
        db.session.commit()
        return jsonify(valid='1', msg='收藏成功！')
    else:
        return jsonify(valid='0', msg='您已收藏过该房源！')


@api.route('/collect_off', methods=['POST'])
def collect_off():
    house_id = request.form.get('house_id')
    user_name = request.form.get('user_name')
    if session.get('user_name') != user_name:
        return jsonify(valid='0', msg='用户验证失败！')
    user = User.query.filter_by(name=user_name).first()
    if not user or not user.collect_id:
        return jsonify(valid='0', msg='操作失败！')
    collect_ids = user.collect_id.split(',')
    if house_id in collect_ids:
        collect_ids.remove(house_id)
        user.collect_id = ','.join(collect_ids)
        db.session.commit()
        return jsonify(valid='1', msg='已取消收藏')
    return jsonify(valid='0', msg='未找到该收藏记录')


@api.route('/del_record', methods=['POST'])
def del_record():
    user_name = request.form.get('user_name')
    if session.get('user_name') != user_name:
        return jsonify(valid='0', msg='用户验证失败！')
    user = User.query.filter_by(name=user_name).first()
    if user:
        user.seen_id = ''
        db.session.commit()
        return jsonify(valid='1', msg='浏览记录已清空')
    return jsonify(valid='0', msg='操作失败')


@api.route('/modify/userinfo/<string:field>', methods=['POST'])
def modify_userinfo(field):
    if 'user_name' not in session:
        return jsonify(ok='0')
    user = User.query.filter_by(name=session['user_name']).first()
    if not user:
        return jsonify(ok='0')
    if field == 'name':
        new_name = request.form.get('name')
        if User.query.filter(User.name == new_name).first():
            return jsonify(ok='0', msg='用户名已存在')
        user.name = new_name
        session['user_name'] = new_name
    elif field == 'addr':
        user.addr = request.form.get('addr')
    elif field == 'pd':
        user.password = request.form.get('pd')
    elif field == 'email':
        user.email = request.form.get('email')
    else:
        return jsonify(ok='0')
    db.session.commit()
    return jsonify(ok='1')


# --- 图表数据API ---
@api.route('/get/scatterdata/<region>')
def get_scatter_data(region):
    return jsonify(data=[[10, 8.04], [8, 6.95], [13, 7.58]])


@api.route('/get/piedata/<region>')
def get_pie_data(region):
    return jsonify(data=[
        {'value': 335, 'name': '2室1厅'},
        {'value': 310, 'name': '3室1厅'},
        {'value': 234, 'name': '1室1厅'}
    ])


@api.route('/get/columndata/<region>')
def get_column_data(region):
    return jsonify(data={
        'x_axis': ['小区A', '小区B', '小区C'],
        'y_axis': [120, 200, 150]
    })


@api.route('/get/brokenlinedata/<region>')
def get_broken_line_data(region):
    return jsonify(data={
        'legend': ['2室1厅', '3室1厅'],
        'x_axis': ['1月', '2月', '3月'],
        'series': [
            {'name': '2室1厅', 'type': 'line', 'data': [3000, 3200, 3100]},
            {'name': '3室1厅', 'type': 'line', 'data': [4500, 4600, 4800]}
        ]
    })


# --- 4. 最后，将配置完成的蓝图注册到主应用 ---
app.register_blueprint(pages)
app.register_blueprint(api, url_prefix='/api')  # 给所有API路由添加 /api 前缀

if __name__ == '__main__':
    app.run(debug=True)