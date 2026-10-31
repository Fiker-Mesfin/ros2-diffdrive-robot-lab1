
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from my_robot_interfaces.action import Rotate


class RotateServer(Node):

    def __init__(self):
        super().__init__('rotate_server')

        self.declare_parameter('turn_speed', 0.5)

        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.odom_group = ReentrantCallbackGroup()
        self.action_group = ReentrantCallbackGroup()

        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10,
            callback_group=self.odom_group
        )

        self.last_yaw = None
        self.total_yaw = 0.0

        self.action_server = ActionServer(
            self,
            Rotate,
            '/rotate',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.action_group
        )

        self.get_logger().info('Rotate action server is ready.')

    def get_yaw(self, orientation):
        sin_yaw = 2.0 * (
            orientation.w * orientation.z +
            orientation.x * orientation.y
        )

        cos_yaw = 1.0 - 2.0 * (
            orientation.y ** 2 +
            orientation.z ** 2
        )

        return math.atan2(sin_yaw, cos_yaw)

    def odom_callback(self, msg):
        yaw = self.get_yaw(msg.pose.pose.orientation)

        if self.last_yaw is not None:
            difference = yaw - self.last_yaw

            difference = math.atan2(
                math.sin(difference),
                math.cos(difference)
            )

            self.total_yaw += difference

        self.last_yaw = yaw

    def goal_callback(self, goal_request):
        if abs(goal_request.angle) < 0.001:
            self.get_logger().warning('Rejecting zero rotation goal.')
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Rotation cancellation requested.')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing rotation goal.')

        requested_angle = goal_handle.request.angle
        turn_speed = self.get_parameter('turn_speed').value

        while self.last_yaw is None:
            time.sleep(0.05)

        start_yaw = self.total_yaw

        cmd = Twist()
        cmd.angular.z = math.copysign(turn_speed, requested_angle)

        feedback_msg = Rotate.Feedback()
        result = Rotate.Result()

        self.publisher.publish(cmd)

        while True:
            if goal_handle.is_cancel_requested:
                self.publisher.publish(Twist())
                goal_handle.canceled()
                result.turned = float(self.total_yaw - start_yaw)
                return result

            turned = self.total_yaw - start_yaw

            feedback_msg.turned = float(turned)
            goal_handle.publish_feedback(feedback_msg)

            if (
                requested_angle > 0 and turned >= requested_angle
            ) or (
                requested_angle < 0 and turned <= requested_angle
            ):
                break

            time.sleep(0.05)

        self.publisher.publish(Twist())

        result.turned = float(self.total_yaw - start_yaw)

        goal_handle.succeed()

        self.get_logger().info(
            f'Rotation completed: {result.turned:.3f} radians.'
        )

        return result


def main(args=None):
    rclpy.init(args=args)

    node = RotateServer()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
