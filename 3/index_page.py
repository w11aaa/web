from flask import Blueprint, render_template, session, redirect, url_for, request
from models import House, User
from settings import db
from sqlalchemy import or_

# 1. 创建一个名为 'pages' 的蓝图
pages = Blueprint('pages', __name__)


# --- 所有渲染页面的路由都移到这里 ---

@pages.route('/')
def index():
    """首页"""
    hot_houses = House.query.order_by(House.page_views.desc()).limit(8).all()
    new_houses = House.query.order_by(House.publish_time.desc()).limit(6).all()
    user_name = session.get('user_name')
    user = User.query.filter_by(name=user_name).first() if user_name else None
    return render_template('index.html', hot_houses=hot_houses, new_houses=new_houses, user=user)


@pages.route('/list/<string:category>/<int:page>')
def house_list(category, page):
    """房源列表页"""
    per_page = 10
    query = House.query
    if category == 'pattern':
        query = query.order_by(House.publish_time.desc())
    elif category == 'hot_house':
        query = query.order_by(House.page_views.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    houses = pagination.items
    user_name = session.get('user_name')
    user = User.query.filter_by(name=user_name).first() if user_name else None
    return render_template('list.html', houses=houses, pagination=pagination, user=user)


@pages.route('/query')
def query():
    """处理搜索请求并跳转到搜索结果列表"""
    addr = request.args.get('addr')
    rooms = request.args.get('rooms')
    session['search_addr'] = addr
    session['search_rooms'] = rooms
    # 注意 url_for 要指向蓝图中的函数
    return redirect(url_for('pages.search_result', page=1))


@pages.route('/search_result/<int:page>')
def search_result(page):
    """显示搜索结果"""
    per_page = 10
    addr = session.get('search_addr', '')
    rooms = session.get('search_rooms', '')
    query = House.query
    if addr:
        query = query.filter(or_(
            House.region.like(f"%{addr}%"),
            House.block.like(f"%{addr}%"),
            House.address.like(f"%{addr}%")
        ))
    if rooms:
        query = query.filter(House.rooms.like(f"%{rooms}%"))
    pagination = query.order_by(House.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    houses = pagination.items
    user_name = session.get('user_name')
    user = User.query.filter_by(name=user_name).first() if user_name else None
    return render_template('list.html', houses=houses, pagination=pagination, user=user)


@pages.route('/house/<int:house_id>')
def house_detail(house_id):
    """房源详情页"""
    house = House.query.get_or_404(house_id)
    house.page_views = (house.page_views or 0) + 1

    user_name = session.get('user_name')
    user = User.query.filter_by(name=user_name).first() if user_name else None
    if user:
        seen_ids = user.seen_id.split(',') if user.seen_id else []
        if str(house_id) not in seen_ids:
            seen_ids.append(str(house_id))
            user.seen_id = ','.join(seen_ids)
    db.session.commit()

    recommendations = House.query.filter(House.address == house.address, House.id != house.id).limit(6).all()
    return render_template('detail_page.html', house=house, recommendations=recommendations, user=user)


@pages.route('/user/<string:username>')
def user_page(username):
    """用户个人主页"""
    if 'user_name' not in session or session['user_name'] != username:
        return redirect(url_for('pages.index'))

    user = User.query.filter_by(name=username).first_or_404()

    collected_houses = []
    if user.collect_id:
        collect_ids = [int(i) for i in user.collect_id.split(',') if i]
        collected_houses = House.query.filter(House.id.in_(collect_ids)).all()

    seen_houses = []
    if user.seen_id:
        seen_ids = [int(i) for i in user.seen_id.split(',') if i]
        seen_houses = House.query.filter(House.id.in_(seen_ids)).all()

    return render_template('user_page.html', user=user, collected_houses=collected_houses, seen_houses=seen_houses)