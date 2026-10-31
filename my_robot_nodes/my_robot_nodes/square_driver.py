
import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

from lab_interfaces.action import DriveDistance
from my_robot_interfaces.action import Rotate


class SquareDriver(Node):

    def __init__(self):
        super().__init__('square_driver')

        self.declare_parameter('side_length', 0.5)
        self.side_length = self.get_parameter('side_length').value

        self.drive_client = ActionClient(
            self,
            DriveDistance,
            '/drive_distance'
        )

        self.rotate_client = ActionClient(
            self,
            Rotate,
            '/rotate'
        )

        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.current_side = 1
        self.odom_received = False

        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.start_timer = self.create_timer(
            1.0,
            self.start_square
        )

        self.get_logger().info(
            'Square driver is waiting for odometry and action servers.'
        )

    def odom_callback(self, msg):
        self.odom_received = True

    def start_square(self):
        if not self.odom_received:
            return

        if (
            self.drive_client.wait_for_server(timeout_sec=0.1)
            and self.rotate_client.wait_for_server(timeout_sec=0.1)
        ):
            self.start_timer.cancel()
            self.get_logger().info('Both action servers are available.')
            self.send_drive_goal()

    def send_drive_goal(self):
        goal = DriveDistance.Goal()
        goal.distance = float(self.side_length)

        self.get_logger().info(
            f'Driving side {self.current_side}/4: '
            f'{self.side_length} meters.'
        )

        future = self.drive_client.send_goal_async(goal)

        future.add_done_callback(
            lambda future: self.drive_goal_response_callback(
                future, self.current_side
            )
        )

    def drive_goal_response_callback(self, future, side):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.fail_square(side, 'Drive goal rejected.')
            return

        self.get_logger().info(f'Side {side}: drive goal accepted.')

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(
            lambda future: self.drive_result_callback(future, side)
        )

    def drive_result_callback(self, future, side):
        response = future.result()

        if (
            response.status != GoalStatus.STATUS_SUCCEEDED
            or not response.result.reached
        ):
            self.fail_square(side, 'Failed to reach the requested distance.')
            return

        self.get_logger().info(
            f'Side {side} completed: '
            f'{response.result.travelled:.3f} meters.'
        )

        self.send_rotate_goal(side)

    def send_rotate_goal(self, side):
        goal = Rotate.Goal()
        goal.angle = math.pi / 2.0

        self.get_logger().info(
            f'Rotating left 90 degrees after side {side}.'
        )

        future = self.rotate_client.send_goal_async(goal)

        future.add_done_callback(
            lambda future: self.rotate_goal_response_callback(
                future, side
            )
        )

    def rotate_goal_response_callback(self, future, side):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.fail_square(side, 'Rotation goal rejected.')
            return

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(
            lambda future: self.rotate_result_callback(future, side)
        )

    def rotate_result_callback(self, future, side):
        response = future.result()

        if response.status != GoalStatus.STATUS_SUCCEEDED:
            self.fail_square(side, 'Rotation failed.')
            return

        self.get_logger().info(
            f'Rotation after side {side} completed: '
            f'{response.result.turned:.3f} radians.'
        )

        if side < 4:
            self.current_side += 1
            self.send_drive_goal()
        else:
            self.get_logger().info(
                'SUCCESS! The robot completed all four sides of the square.'
            )
            self.publisher.publish(Twist())

    def fail_square(self, side, message):
        self.publisher.publish(Twist())

        self.get_logger().error(
            f'Square failed at side {side}: {message}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = SquareDriver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
