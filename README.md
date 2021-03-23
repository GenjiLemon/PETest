# 高校体测数据管理系统

## 项目简介

高校体测抽测使用平台，包括体测项目导入、学校学生导入、学生成绩计算导出、学校成绩分析等功能。

## 运行条件

- python3.8+
- MySQL5.7+
- 最好在linux部署



## 运行说明

- 下载/clone源码
- 执行 pip -r requirements.txt 安装所需文件
- 配置数据库
- python run启动，默认端口5000



## 技术架构

前端采用Layuimini，后端使用python著名web框架Flask，layuimini的页面放在template目录，api文件实现前后端分离的代码，路由文件具有简单的模板渲染。

## 感谢

感谢开源项目Layuimini，优秀前端框架Layui，感谢python著名web框架Flask。
