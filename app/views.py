from app import app
from .province import province
from .school import school
from .api import api
from app import main
#这里分别给app注册了两个蓝图admin,school
#参数url_prefix='/xxx'的意思是设置request.url中的url前缀，
#即当request.url是以/admin或者/user的情况下才会通过注册的蓝图的视图方法处理请求并返回
app.register_blueprint(province,url_prefix='/province')
app.register_blueprint(school, url_prefix='/school')
app.register_blueprint(api, url_prefix='/api')