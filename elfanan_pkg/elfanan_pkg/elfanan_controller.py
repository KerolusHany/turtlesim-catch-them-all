#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math
from my_robot_interfaces.msg import Turtle, TurtleArray
from my_robot_interfaces.srv import CatchTurtle
from functools import partial

class Elfanan(Node):
    def __init__(self):
        super().__init__("elfanan_controller")
        self.declare_parameter("catch_closest_turtle_first", True)
        self.turtle_to_catch_ = None
        self.pose_: Pose = None
        self.catch_closest_ = self.get_parameter("catch_closest_turtle_first").value
        self.cmd_vel_publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.pose_subscriber_ = self.create_subscription(Pose, "/turtle1/pose", self.callback_pose, 10)
        self.alive_turtles_subscriber_ = self.create_subscription(TurtleArray, "alive_turtles", self.callback_alive_turtles, 10)
        self.catch_turtle_client_ = self.create_client(CatchTurtle, "catch_turtle")
        self.control_loop_timer_ = self.create_timer(0.01, self.control_loop)

    def callback_alive_turtles(self, msg: TurtleArray):
        if self.pose_ is None:
            return
        if len(msg.turtles) > 0:
            if self.catch_closest_:
                closest_turtle = None
                closest_turtle_distance = None
                for turtle in msg.turtles:
                    dist_x = turtle.x - self.pose_.x
                    dist_y = turtle.y - self.pose_.y
                    distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
                    if closest_turtle is None or distance < closest_turtle_distance:
                        closest_turtle = turtle
                        closest_turtle_distance = distance
                self.turtle_to_catch_ = closest_turtle
            else:
                self.turtle_to_catch_ = msg.turtles[0]
        else:
            self.turtle_to_catch_ = None

    def callback_pose(self, pose: Pose):
        self.pose_ = pose

    def control_loop(self):
        if self.pose_ is None or self.turtle_to_catch_ is None:
            return
        dist_x = self.turtle_to_catch_.x - self.pose_.x
        dist_y = self.turtle_to_catch_.y - self.pose_.y
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
        cmd = Twist()
        if distance > 0.5:
            cmd.linear.x = 2.0 * distance
            goal_theta = math.atan2(dist_y, dist_x)
            diff = goal_theta - self.pose_.theta
            if diff > math.pi:
                diff -= 2 * math.pi
            elif diff < -math.pi:
                diff += 2 * math.pi
            cmd.angular.z = 6.0 * diff
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.call_catch_service(self.turtle_to_catch_.name)
            self.turtle_to_catch_ = None
        self.cmd_vel_publisher_.publish(cmd)

    def call_catch_service(self, turtle_name):
        while not self.catch_turtle_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Waiting for catch_turtle service...")
        request = CatchTurtle.Request()
        request.name = turtle_name
        future = self.catch_turtle_client_.call_async(request)
        future.add_done_callback(partial(self.callback_call_catch_turtle_srv, turtle_name=turtle_name))

    def callback_call_catch_turtle_srv(self, future, turtle_name):
        try:
            response = future.result()
            if not response.success:
                self.get_logger().error(f"Turtle {turtle_name} could not be removed.")
            else:
                self.get_logger().info(f"Caught turtle: {turtle_name}")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = Elfanan()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
