import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from lab_interfaces.msg import ObstacleInfo
from my_robot_interfaces.msg import RobotStatus
from std_srvs.srv import SetBool
from my_robot_interfaces.srv import SetTurnSpeed
class TurnAway(Node):

    def __init__(self):
        super().__init__('turn_away')
        self.declare_parameter('forward_speed', 0.2)
        self.declare_parameter('turn_speed', 0.5)
        self.declare_parameter('max_turn_speed', 1.5)

        self.turn_speed_service = self.create_service(
            SetTurnSpeed,
            '/set_turn_speed',
            self.set_turn_speed_callback
        )
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        self.status_publisher = self.create_publisher(
            RobotStatus,
            '/robot_status',
            10
        )
        self.enabled = False

        self.enable_service = self.create_service(
            SetBool,
            '/turn_away_enable',
            self.enable_callback
        )
        self.subscription = self.create_subscription(
            ObstacleInfo,
            '/obstacle',
            self.obstacle_callback,
            10
        )

        self.get_logger().info('Turn away node started.')

    def obstacle_callback(self, msg):
        forward_speed = self.get_parameter('forward_speed').value
        turn_speed = self.get_parameter('turn_speed').value
        if not self.enabled:
            status = RobotStatus()
            status.state = 'stopped'
            status.obstacle_distance = msg.distance
            self.status_publisher.publish(status)
            return
        cmd = Twist()

        if not msg.too_close:
            cmd.linear.x = forward_speed
            cmd.angular.z = 0.0

        else:
            cmd.linear.x = 0.0

            if msg.angle >= 0:
                cmd.angular.z = -turn_speed
            else:
                cmd.angular.z = turn_speed

        self.publisher.publish(cmd)
        status = RobotStatus()
        status.obstacle_distance = msg.distance

        if msg.too_close:
            status.state = 'turning'
        else:
            status.state = 'forward'

        self.status_publisher.publish(status)
    def enable_callback(self, request, response):
        if not request.data:
            if self.enabled:
                self.publisher.publish(Twist())

            self.enabled = False
            response.success = True
            response.message = 'Turn away disabled.'

        else:
            self.enabled = True
            response.success = True
            response.message = 'Turn away enabled.'

        self.get_logger().info(response.message)
        return response
    def set_turn_speed_callback(self, request, response):
        max_speed = self.get_parameter('max_turn_speed').value

        if request.turn_speed <= 0 or request.turn_speed > max_speed:
            response.success = False
            response.message = f'Turn speed must be greater than 0 and at most {max_speed}.'
        else:
            self.set_parameters([
                rclpy.parameter.Parameter(
                    'turn_speed',
                    rclpy.Parameter.Type.DOUBLE,
                    float(request.turn_speed)
                )
            ])

            response.success = True
            response.message = f'Turn speed updated to {request.turn_speed}.'

        self.get_logger().info(response.message)
        return response
def main(args=None):
    rclpy.init(args=args)

    node = TurnAway()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
