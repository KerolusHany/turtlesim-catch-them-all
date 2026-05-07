#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, Kill
from functools import partial
import random
import math
from my_robot_interfaces.msg import Turtle, TurtleArray
from my_robot_interfaces.srv import CatchTurtle

class Spawner(Node): 
    def __init__(self):
        super().__init__("elfanan_spawner")

        self.declare_parameter("turtle_name","turtle")
        self.declare_parameter("turtle_frequency", 1.0)

        self.turtle_name_prefix_ = self.get_parameter("turtle_name").value
        self.spawn_frequency_ = self.get_parameter("turtle_frequency").value
        self.turtle_counter_ = 0
        self.alive_turtles_ = []

        self.alive_turtles_pub_ = self.create_publisher(TurtleArray, "alive_turtles", 10)

        self.spawn_client_ = self.create_client(Spawn, "/spawn")
        self.kill_client_ = self.create_client(Kill, "/kill")

        self.catch_turtle_service_ = self.create_service(
            CatchTurtle, "catch_turtle", self.callback_catch_turtle
        )

        self.spawn_turtle_timer_ = self.create_timer(self.spawn_frequency_, self.spawn_new_turtle)


    def callback_catch_turtle(self, request, response):
        self.call_kill_service(request.name)
        response.success = True
        return response


    def publish_alive_turtles(self):
        msg = TurtleArray()
        msg.turtles = self.alive_turtles_
        self.alive_turtles_pub_.publish(msg)

    def spawn_new_turtle(self):
        self.turtle_counter_ += 1
        name = self.turtle_name_prefix_ + str(self.turtle_counter_)

        x = random.uniform(1.0, 10.0)
        y = random.uniform(1.0, 10.0)
        theta = random.uniform(0.0, 2 * math.pi)

        self.call_spawn_service(name, x, y, theta)

    def call_spawn_service(self, turtle_name, x, y, theta):
        while not self.spawn_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Waiting for /spawn service...")

        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = turtle_name

        future = self.spawn_client_.call_async(request)
        future.add_done_callback(partial(self.callback_call_spawn_service, request=request))

    def callback_call_spawn_service(self, future, request):
        response = future.result()
        if response is None:
            self.get_logger().error("Spawn service failed!")
            return

        if response.name != "":
            self.get_logger().info(f"New turtle spawned: {response.name}")
            new_turtle = Turtle()
            new_turtle.name = response.name
            new_turtle.x = request.x
            new_turtle.y = request.y
            self.alive_turtles_.append(new_turtle)
            self.publish_alive_turtles()

    def call_kill_service(self, turtle_name):
        while not self.kill_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Waiting for /kill service...")

        request = Kill.Request()
        request.name = turtle_name

        future = self.kill_client_.call_async(request)
        future.add_done_callback(partial(self.callback_call_kill_service, turtle_name=turtle_name))

    def callback_call_kill_service(self, future, turtle_name):
        try:
            future.result()  # execute the kill
            self.get_logger().info(f"Turtle {turtle_name} killed successfully!")
        except Exception as e:
            self.get_logger().error(f"Failed to kill {turtle_name}: {e}")
            return

        # remove from alive list
        for i, turtle in enumerate(self.alive_turtles_):
            if turtle.name == turtle_name:
                del self.alive_turtles_[i]
                break

        self.publish_alive_turtles()

def main(args=None):
    rclpy.init(args=args)
    node = Spawner() 
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
