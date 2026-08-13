<div align="right">

[简体中文](README_CN.md)|[English](README.md)

</div>

<div align="center">

# 睿尔曼机器人rm_bringup使用说明书V1.7

睿尔曼智能科技（北京）有限公司
文件修订记录：

| 版本号| 时间   | 备注  | 
| :---: | :-----: | :---: |
|V1.0    |2024-2-19  |拟制 |
|V1.1    |2024-7-8   |修订(添加GEN72适配文件) |
|V1.2    |2024-9-10  |修订(添加ECO63适配文件) |
|V1.3    |2024-12-25 |修订(添加了63、65、75、ECO65的六维力适配文件，以及63、65、75、ECO63、ECO65的一体化六维力适配文件) |
|V1.4    |2025-4-7 |修订(添加了GEN72_II适配文件) |
|V1.5    |2025-11-13 |修订(添加了RML63_III适配文件) |
|V1.6    |2026-4-16 |修订(添加ECO62、RX75适配文件) |
|V1.7    |2026-8-13 |修订(新增统一启动入口和按型号解析的 `arm_variant:=auto` 默认值) |

</div>

## 目录
* 1.[rm_bringup功能包说明](#rm_bringup功能包说明)
* 2.[rm_bringup功能包使用](#rm_bringup功能包使用)
* 2.1[moveit2控制真实机械臂](#moveit2控制真实机械臂)
* 2.2[控制gazebo仿真机械臂](#控制gazebo仿真机械臂)
* 3.[rm_bringup功能包架构说明](#rm_bringup功能包架构说明)
* 3.1[功能包文件总览](#rm_bringup功能包架构说明)
* 4.[rm_bringup话题说明](#rm_bringup话题说明)

## rm_bringup功能包说明
rm_bringup功能包为实现多个launch文件同时运行所设计的功能包，使用该功能包可用一条命令实现多个节点结合的复杂功能的启动。
* 1.功能包使用。
* 2.功能包架构说明。
* 3.功能包话题说明。  
通过这三部分内容的介绍可以帮助大家：
* 1.了解该功能包的使用。
* 2.熟悉功能包中的文件构成及作用。
* 3.熟悉功能包相关的话题，方便开发和使用
## rm_bringup功能包使用
### 统一启动入口
推荐使用 `rm_bringup.launch.py`，通过参数选择机械臂、末端版本和运行模式；原有按型号拆分的 launch 命令继续兼容。

```bash
ros2 launch rm_bringup rm_bringup.launch.py \
  arm_type:=65 arm_variant:=6f mode:=gazebo
```

| 参数 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `arm_type` | 无，必须指定 | `63/63_iii/65/75/eco62/eco63/eco65/gen72/gen72_ii/rx75` |
| `arm_variant` | `auto` | RX75自动解析为 `6fb`，其他型号自动解析为 `standard`；也可显式选择型号支持的 `standard/6f/6fb/6fb_v` |
| `mode` | `real` | `real` 或 `gazebo` |
| `allow_trajectory_execution` | `true` | 是否允许 MoveIt 执行轨迹；设为 `false` 时仅规划，不执行 |
| `use_moveit` | `true` | 是否启动 MoveIt；为 `false` 时还需设置 `use_rviz:=false` |
| `use_rviz` | `true` | 是否启动 MoveIt RViz |
| `driver_config` | `auto` | 真机单臂 driver YAML；RX75 请使用左右两项 |
| `left_driver_config` | `auto` | RX75 左臂 driver YAML |
| `right_driver_config` | `auto` | RX75 右臂 driver YAML |
| `follow` | `auto` | 真机控制跟随模式：`auto/true/false` |
| `joint_states_topic` | `auto` | 当前仅支持 `auto`，按型号和模式选择默认 joint states Topic |
| `start_gazebo` | `true` | Gazebo 模式下是否启动仿真进程 |

支持的型号与末端版本如下：

| 型号 | 支持版本 |
| :--- | :--- |
| `63` | `standard`, `6f`, `6fb` |
| `63_iii` | `standard`, `6fb` |
| `65` | `standard`, `6f`, `6fb` |
| `75` | `standard`, `6f`, `6fb` |
| `eco62` | `standard` |
| `eco63` | `standard`, `6fb` |
| `eco65` | `standard`, `6f`, `6fb` |
| `gen72` | `standard` |
| `gen72_ii` | `standard` |
| `rx75` | `6fb`, `6fb_v` |

不支持的组合会在任何节点启动前直接报错。例如，ECO62 不提供 `6fb` 统一入口。真实机械臂联调时可临时传入 `allow_trajectory_execution:=false`，该设置不会修改默认值。

使用 `arm_type:=rx75` 且不传 `arm_variant` 时，统一入口默认选择RX75-6FB；RX75-6FB-V需显式传入 `arm_variant:=6fb_v`。

统一入口现在直接组合 `rm_driver`、`rm_description`、`rm_control` 和
`rm_gazebo` 的通用 launch，而不是再跳转到某个型号的旧 bringup 文件。
原有 42 个按型号入口已改成薄兼容 wrapper，旧命令及 RX75 的
`use_moveit_rviz` 参数继续可用。Gazebo 仍按历史行为在 8 秒后启动
MoveIt；controller readiness 时序优化将在后续独立实施。

### moveit2控制真实机械臂
首先配置好环境完成连接后我们可以通过以下命令直接启动节点，运行rm_bringup功能包中的launch.py文件。
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_<arm_type>_bringup.launch.py
```
在实际使用时需要将以上的<arm_type>更换为实际的机械臂型号，可选择的机械臂型号有65、63、63_III、75、eco62、eco63、eco65、gen72、gen72_II、rx75。

启动六维力版本机械臂的命令为（当前支持63、65、75、eco65）：
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_<arm_type>_6f_bringup.launch.py
```
启动一体化六维力版本机械臂的命令为（当前支持63、63_III、65、75、eco63、eco65、rx75）：
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_<arm_type>_6fb_bringup.launch.py
```
启动带视觉方案的六维力版本机械臂的命令为（当前仅支持rx75）：
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_<arm_type>_6fb_v_bringup.launch.py
```
例如65机械臂的启动命令：
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_65_bringup.launch.py
```
节点启动成功后，将弹出以下画面。
![image](doc/rm_bringup1.png)  
该launch文件会启动MoveIt 2控制真实机械臂的功能，随后可使用控制球规划机械臂运动，详细内容见《[rm_moveit2_config详解](../rm_moveit2_config/README_CN.md)》。
### 控制gazebo仿真机械臂
我们可以通过以下命令运行rm_bringup功能包中的launch.py文件，直接启动其中的gzaebo仿真节点。
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_<arm_type>_gazebo.launch.py
```
在实际使用时需要将以上的<arm_type>更换为实际的机械臂型号，可选择的机械臂型号有65、63、63_III、75、eco62、eco63、eco65、gen72、gen72_II、rx75。

启动六维力版本机械臂的命令为（当前支持63、65、75、eco65）：
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_<arm_type>_6f_gazebo.launch.py
```
启动一体化六维力版本机械臂的命令为（当前支持63、63_III、65、75、eco63、eco65、rx75）：
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_<arm_type>_6fb_gazebo.launch.py
```
启动带视觉方案的六维力版本机械臂的命令为（当前仅支持rx75）：
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_<arm_type>_6fb_v_gazebo.launch.py
```
例如65机械臂的启动命令：
```
rm@rm-desktop:~$ ros2 launch rm_bringup rm_65_gazebo.launch.py
```
节点启动成功后，将弹出以下画面。
![image](doc/rm_bringup2.png)  
之后我们使用如下指令启动moveit2控制gazebo中的仿真机械臂。
![image](doc/rm_bringup3.png)
## rm_bringup功能包架构说明
### 功能包文件总览
当前rm_bringup功能包的文件构成如下。
```
├── CMakeLists.txt                      #编译规则文件
├── doc                                 #辅助文档、图片存放文件夹
│   ├── rm_bringup1.png                 #图片1
│   ├── rm_bringup2.png                 #图片2
│   └── rm_bringup3.png                 #图片3
├── launch                              #启动文件
│   ├── rm_bringup.launch.py             #所有支持型号、末端版本和运行模式的统一启动入口
│   ├── rm_63_6f_bringup.launch.py      #63臂六维力moveit2启动文件
│   ├── rm_63_6f_gazebo.launch.py       #63臂六维力gazebo启动文件
│   ├── rm_63_6fb_bringup.launch.py     #63臂一体化六维力moveit2启动文件
│   ├── rm_63_6fb_gazebo.launch.py      #63臂一体化六维力gazebo启动文件
│   ├── rm_63_bringup.launch.py         #63臂moveit2启动文件
│   ├── rm_63_gazebo.launch.py          #63臂gazebo启动文件
│   ├── rm_63_III_bringup.launch.py     #63_III臂moveit2启动文件
│   ├── rm_63_III_gazebo.launch.py      #63_III臂gazebo启动文件
│   ├── rm_63_III_6fb_bringup.launch.py #63_III臂六维力moveit2启动文件
│   ├── rm_63_III_6fb_gazebo.launch.py  #63_III臂六维力gazebo启动文件
│   ├── rm_65_6f_bringup.launch.py      #65臂六维力moveit2启动文件
│   ├── rm_65_6f_gazebo.launch.py       #65臂六维力gazebo启动文件
│   ├── rm_65_6fb_bringup.launch.py     #65臂一体化六维力moveit2启动文件
│   ├── rm_65_6fb_gazebo.launch.py      #65臂一体化六维力gazebo启动文件
│   ├── rm_65_bringup.launch.py         #65臂moveit2启动文件
│   ├── rm_65_gazebo.launch.py          #65臂gazebo启动文件
│   ├── rm_75_6f_bringup.launch.py      #75臂六维力moveit2启动文件
│   ├── rm_75_6f_gazebo.launch.py       #75臂六维力gazebo启动文件
│   ├── rm_75_6fb_bringup.launch.py     #75臂一体化六维力moveit2启动文件
│   ├── rm_75_6fb_gazebo.launch.py      #75臂一体化六维力gazebo启动文件
│   ├── rm_75_bringup.launch.py         #75臂moveit2启动文件
│   ├── rm_75_gazebo.launch.py          #75臂gazebo启动文件
│   ├── rm_eco62_bringup.launch.py      #eco62臂moveit2启动文件
│   ├── rm_eco62_gazebo.launch.py       #eco62臂gazebo启动文件
│   ├── rm_eco63_6fb_bringup.launch.py  #eco63臂一体化六维力moveit2启动文件
│   ├── rm_eco63_6fb_gazebo.launch.py   #eco63臂一体化六维力gazebo启动文件
│   ├── rm_eco63_bringup.launch.py      #eco63臂moveit2启动文件
│   ├── rm_eco63_gazebo.launch.py       #eco63臂gazebo启动文件
│   ├── rm_eco65_6f_bringup.launch.py   #eco65臂六维力moveit2启动文件
│   ├── rm_eco65_6f_gazebo.launch.py    #eco65臂六维力gazebo启动文件
│   ├── rm_eco65_6fb_bringup.launch.py  #eco65臂一体化六维力moveit2启动文件
│   ├── rm_eco65_6fb_gazebo.launch.py   #eco65臂一体化六维力gazebo启动文件
│   ├── rm_eco65_bringup.launch.py      #eco65臂moveit2启动文件
│   ├── rm_eco65_gazebo.launch.py       #eco65臂gazebo启动文件
│   ├── rm_gen72_bringup.launch.py      #gen72臂moveit2启动文件
│   ├── rm_gen72_gazebo.launch.py       #gen72臂gazebo启动文件
│   ├── rm_gen72_II_bringup.launch.py   #gen72_II臂moveit2启动文件
│   ├── rm_gen72_II_gazebo.launch.py    #gen72_II臂gazebo启动文件
│   ├── rm_rx75_6fb_bringup.launch.py   #RX75-6FB双臂moveit2启动文件
│   ├── rm_rx75_6fb_gazebo.launch.py    #RX75-6FB双臂gazebo启动文件
│   ├── rm_rx75_6fb_v_bringup.launch.py #RX75-6FB-V双臂moveit2启动文件
│   └── rm_rx75_6fb_v_gazebo.launch.py  #RX75-6FB-V双臂gazebo启动文件
├── rm_bringup                         #统一启动入口使用的Python模块
│   ├── __init__.py                      #Python包标记文件
│   ├── legacy_bringup.py                #42个旧入口的兼容wrapper工厂
│   └── variant_catalog.py               #型号能力、别名、组件映射与组合校验
├── package.xml                         #依赖说明文件
├── README_CN.md                        #中文说明文档
└── README.md                           #英文说明文档
```
## rm_bringup话题说明
该功能包当前没有自身话题，主要用于启动其他功能包。MoveIt 2相关接口见《[rm_moveit2_config详解](../rm_moveit2_config/README_CN.md)》。
