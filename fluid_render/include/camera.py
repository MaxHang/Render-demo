import math
from enum import Enum, auto

import glm

# 摄像机参数默认值
ZOOM = 45.0
SPEED = 2.5
YAW = -90.0
PITCH = 0.0
SENSITIVITY = 0.1

# Defines several possible options for camera movement. Used as abstraction to stay away from window-system specific input methods
class CameraMovement(Enum):
    LEFT = auto()
    RIGHT = auto()
    FORWARD = auto()
    BACKWARD = auto()


class Camera:

    def __init__(self, position=glm.vec3([0.0, 0.0, 0.0]), up=glm.vec3([0, 1, 0]), yaw=YAW, pitch=PITCH):
        # 摄像机位置
        self.position = position
        # 摄像机空间
        self.front = glm.vec3([0.0, 0.0, -1.0])
        self.right = glm.vec3()
        self.up = glm.vec3()
        # 世界空间中 向上 的向量, 用于计算摄像机空间的right
        self.world_up = up
        # 偏航角以及俯仰角
        self.yaw = yaw
        self.pitch = pitch
        # 视野
        self.zoom = ZOOM
        # 鼠标移动速度
        self.m_movement_speed = SPEED
        # 鼠标灵敏度值
        self.m_mouse_sensitivity = SENSITIVITY

        self.update_camera_vectors()

    def get_view_matrix(self):
        """
        returns the view matrix calculated using Euler Angles and the LookAt Matrix
        """
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def get_zoom(self):
        return self.zoom

    def get_pos(self):
        return self.position

    def process_keyboard(self, direction, delta_time):
        """processes input received from any keyboard-like input system. Accepts input parameter in the form of camera defined ENUM (to abstract it from windowing systems)

        :param direction: 移动方向
        :param delta_time: 渲染上一帧所需时间
        """
        velocity = self.m_movement_speed * delta_time

        if (direction == CameraMovement.FORWARD):
            self.position += self.front * velocity
        if (direction == CameraMovement.BACKWARD):
            self.position -= self.front * velocity
        if (direction == CameraMovement.LEFT):
            self.position -= self.right * velocity
        if (direction == CameraMovement.RIGHT):
            self.position += self.right * velocity
        # make sure the user stays at the ground level
        # self.position.y = 0.0

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        """
        processes input received from a mouse input system. Expects the offset value in both the x and y direction.
        """
        xoffset *= self.m_mouse_sensitivity
        yoffset *= self.m_mouse_sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))

        self.update_camera_vectors()

    def process_mouse_scroll(self, yoffset):
        """
        processes input received from a mouse scroll-wheel event. Only requires input on the vertical wheel-axis
        """
        if self.zoom >= 1.0 and self.zoom <= 89.0:
            self.zoom -= yoffset

        self.zoom = max(1.0, min(89.0, self.zoom))

    def update_camera_vectors(self):
        """
        calculates the front vector from the Camera's (updated) Euler Angles
        """

        # -- calc front vector
        front = glm.vec3()
        front.x = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front.y = math.sin(math.radians(self.pitch))
        front.z = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.front = glm.normalize(front)

        # -- recalc right and up
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def print_camera_position(self):
        """输出摄像机位置"""
        print(f'camera position: {self.position}')
