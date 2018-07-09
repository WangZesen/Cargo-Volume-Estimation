# Cargo-Volume-Estimation

## Description
Capstone Design 

Estimate Cargo Volume using Kinect under the environment of conveyor belt

## Environment Setting

1. Opencv 3.3.0
2. libfreenect2
3. pylibfreenect2

Detail: https://docs.google.com/document/d/1G0t_qg3npnhR9EYVWwBvk8fxgYTYJX08fPgjS-Lj6YI/edit?usp=sharing

## Todo:
- [x] 深度图降噪
- [x] 根据深度图生成点云
- [x] 去除背景
- [x] 判断闪光带位置
- [x] 利用闪光带判断什么时候拍照
- [x] 单相机多张照片合并(闪光带定位)
- [ ] 双相机产生的两个点云合并
- [ ] 需要一个Python的高效实时显示点云的库 (mayavi, moviepy可用,但需要Python3)

## Run:

<pre><code>cd work
sudo python main.py
</code></pre>

## Data

Point Cloud Sample Data: https://jbox.sjtu.edu.cn/l/b1kxkP
