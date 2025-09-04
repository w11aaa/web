from flask import request, jsonify, redirect, url_for, session, Blueprint
from settings import app, db
from models import User, House
from sqlalchemy import or_, func, and_
import re
import time

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


def clean_price(price_str):
    """从价格字符串（如 '3500元/月'）中提取数值"""
    if not price_str:
        return 0
    match = re.search(r'(\d+(\.\d+)?)', str(price_str))
    return float(match.group(1)) if match else 0


def build_location_query_filter(region_str):
    """
    【优化】根据'区-街道-小区'格式的字符串构建更精确的查询条件
    """
    parts = region_str.split('-')
    region_part = parts[0].replace('区', '') if len(parts) > 0 else ''
    block_part = parts[1] if len(parts) > 1 else ''
    address_part = parts[2] if len(parts) > 2 else ''  # 新增：处理第三部分（小区）

    conditions = []
    if region_part:
        conditions.append(House.region.like(f"%{region_part}%"))
    if block_part:
        conditions.append(House.block.like(f"%{block_part}%"))
    # 如果有小区信息，则加入查询条件，使定位更精确
    if address_part:
        conditions.append(House.address.like(f"%{address_part}%"))

    return and_(*conditions)


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


# --- 图表数据API (已修正查询逻辑) ---
@api.route('/get/scatterdata/<region>')
def get_scatter_data(region):
    print(f"--- [散点图] 正在查询复合区域: {region} ---")
    location_filter = build_location_query_filter(region)
    query = House.query.filter(location_filter).limit(100).all()
    print(f"[散点图] 数据库查询到 {len(query)} 条原始记录")
    data = []
    for house in query:
        try:
            area_match = re.search(r'(\d+(\.\d+)?)', str(house.area))
            if area_match:
                area = float(area_match.group(1))
                price = clean_price(house.price)
                if area > 0 and price > 0:
                    data.append([area, price])
        except (ValueError, TypeError, AttributeError):
            continue
    print(f"[散点图] 清洗后得到 {len(data)} 条有效数据")
    return jsonify(data=data)


@api.route('/get/piedata/<region>')
def get_pie_data(region):
    print(f"--- [饼图] 正在查询复合区域: {region} ---")
    location_filter = build_location_query_filter(region)
    query_result = db.session.query(
        House.rooms, func.count(House.id)
    ).filter(
        location_filter
    ).group_by(House.rooms).order_by(func.count(House.id).desc()).limit(5).all()
    print(f"[饼图] 数据库查询到 {len(query_result)} 条分组记录")
    data = [{'value': count, 'name': rooms} for rooms, count in query_result if rooms]
    print(f"[饼图] 清洗后得到 {len(data)} 条有效数据")
    return jsonify(data=data)


@api.route('/get/columndata/<region>')
def get_column_data(region):
    print(f"--- [柱状图] 正在查询复合区域: {region} ---")
    location_filter = build_location_query_filter(region)
    # 【修复】按 address (小区) 分组, 而不是 block (街道)
    top_communities_subquery = db.session.query(
        House.address, func.count(House.id).label('house_count')
    ).filter(
        location_filter, House.address.isnot(None)
    ).group_by(House.address).order_by(func.count(House.id).desc()).limit(5).subquery()

    top_communities = db.session.query(top_communities_subquery).all()
    print(f"[柱状图] 查询到 {len(top_communities)} 个热门小区")

    if not top_communities:
        return jsonify(data={'x_axis': [], 'y_axis': []})

    community_names = [c.address for c in top_communities]
    # 【修复】查询条件应包含 location_filter 以确保数据范围正确
    houses_in_top_communities = db.session.query(House).filter(
        location_filter, House.address.in_(community_names)
    ).all()

    community_prices = {name: [] for name in community_names}
    for house in houses_in_top_communities:
        price = clean_price(house.price)
        if price > 0 and house.address in community_prices:
            community_prices[house.address].append(price)

    x_axis = list(community_prices.keys())
    y_axis = [round(sum(prices) / len(prices), 2) if prices else 0 for prices in community_prices.values()]

    print(f"[柱状图] 计算出 {len(x_axis)} 个小区的平均价格")
    return jsonify(data={'x_axis': x_axis, 'y_axis': y_axis})


@api.route('/get/brokenlinedata/<region>')
def get_broken_line_data(region):
    print(f"--- [折线图] 正在查询复合区域: {region} ---")
    location_filter = build_location_query_filter(region)
    room_types = ['2室1厅', '3室1厅']
    series = []

    # 【修复】移除30天的时间限制, 以适应旧数据
    # thirty_days_ago = int(time.time()) - 30 * 24 * 60 * 60

    for room_type in room_types:
        query = db.session.query(House.price).filter(
            location_filter,
            House.rooms == room_type
            # House.publish_time > thirty_days_ago
        ).order_by(House.publish_time.asc()).all()

        print(f"[折线图] 查询到 '{room_type}' {len(query)} 条记录")
        prices = [clean_price(p[0]) for p in query if clean_price(p[0]) > 0]

        if prices:
            series.append({'name': room_type, 'type': 'line', 'data': prices})

    max_len = max((len(s['data']) for s in series), default=0)
    x_axis_labels = [f"数据点 {i + 1}" for i in range(max_len)]

    return jsonify(data={
        'legend': [s['name'] for s in series],
        'x_axis': x_axis_labels,
        'series': series
    })


# --- 4. 最后，将配置完成的蓝图注册到主应用 ---
app.register_blueprint(pages)
app.register_blueprint(api, url_prefix='/api')  # 给所有API路由添加 /api 前缀

if __name__ == '__main__':
    app.run(debug=True)

