import glm
import math
from enum import Enum, auto


#Default camera values
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
        self.position = position
        self.front = glm.vec3([0.0, 0.0, -1.0])
        # 世界空间中 向上 的向量
        self.world_up = up

        self.yaw = yaw
        self.pitch = pitch

        self.zoom = ZOOM
        self.movement_speed = SPEED
        self.mouse_sensitivity = SENSITIVITY

        self.update_camera_vectors()

    def get_view_matrix(self):
        """
        returns the view matrix calculated using Euler Angles and the LookAt Matrix
        """
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def process_keyboard(self, direction, delta_time):
        """
        processes input received from any keyboard-like input system. Accepts input parameter in the form of camera defined ENUM (to abstract it from windowing systems)
        """
        velocity = self.movement_speed * delta_time

        dir_vector = {
            CameraMovement.LEFT : -self.right * velocity,
            CameraMovement.RIGHT : self.right * velocity,
            CameraMovement.FORWARD : self.front * velocity,
            CameraMovement.BACKWARD : -self.front * velocity,
        }.get(direction)
        self.position += dir_vector
        # make sure the user stays at the ground level
        # self.position.y = 0.0

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        """
        processes input received from a mouse input system. Expects the offset value in both the x and y direction.
        """
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))

        self.update_camera_vectors()

    def process_mouse_scroll(self, yoffset):
        """
        processes input received from a mouse scroll-wheel event. Only requires input on the vertical wheel-axis
        """
        if self.zoom >= 1.0 and self.zoom <= 45.0:
            self.zoom -= yoffset

        self.zoom = max(1.0, min(45.0, self.zoom))

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
