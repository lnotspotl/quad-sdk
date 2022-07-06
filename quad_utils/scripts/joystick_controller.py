#!/usr/bin/env python

import rospy
from math import fabs
from numpy import array_equal

from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from std_msgs.msg import UInt8

class PS4_controller(object):
    def __init__(self, rate):
        rospy.init_node("twist_publisher")
        rospy.Subscriber("joy", Joy, self.callback)
        self.twist_publisher = rospy.Publisher("robot_1/cmd_vel", Twist, queue_size = 10)
        self.uint8_publisher = rospy.Publisher("robot_1/control/mode", UInt8, queue_size = 1)
        self.rate = rospy.Rate(rate)

        # target
        self.target_joy = Joy()
        self.target_joy.axes = [0.,0.,1.,0.,0.,1.,0.,0.]
        self.target_joy.buttons = [0,0,0,0,0,0,0,0,0,0,0]

        # last
        self.last_joy = Joy()
        self.last_joy.axes = [0.,0.,1.,0.,0.,1.,0.,0.]
        self.last_joy.buttons = [0,0,0,0,0,0,0,0,0,0,0]
        self.last_send_time = rospy.Time.now()

        self.use_button = True
        self.speed = 3.0;

        self.control_mode = 0

    def run(self):
        while not rospy.is_shutdown():
            self.publish_joy()
            self.rate.sleep()

    def callback(self, msg):
        self.target_joy.axes = msg.axes
        self.target_joy.buttons = msg.buttons

        if(self.use_button and msg.buttons[3]):
            self.use_button = False
            uint8_msg = UInt8()
            if(self.control_mode == 1):
                self.control_mode = 0
            elif(self.control_mode == 0):
                self.control_mode = 1

            uint8_msg.data = self.control_mode
            self.uint8_publisher.publish(uint8_msg)


        if(not self.use_button and not msg.buttons[3]):
            self.use_button = True

    def ramped_vel(self,v_prev,v_target,t_prev,t_now):
        # https://github.com/osrf/rosbook/blob/master/teleop_bot/keys_to_twist_with_ramps.py
        step = (t_now - t_prev).to_sec()
        sign = self.speed if \
                (v_target > v_prev) else -self.speed
        error = fabs(v_target - v_prev)

        # if we can get there within this timestep -> we're done.
        if error < self.speed*step:
            return v_target
        else:
            return v_prev + sign * step # take a step toward the target

    def publish_joy(self):
        t_now = rospy.Time.now()

        # determine changes in state
        axes_updated = not array_equal(self.last_joy.axes, self.target_joy.axes)

        joy = Joy()
        if axes_updated:
            # do ramped_vel for every single axis
            for i in range(len(self.target_joy.axes)): 
                if self.target_joy.axes[i] == self.last_joy.axes[i]:
                    joy.axes.append(self.last_joy.axes[i])
                else:
                    joy.axes.append(self.ramped_vel(self.last_joy.axes[i],
                            self.target_joy.axes[i],self.last_send_time,t_now))
        else:
            joy.axes = self.last_joy.axes

        joy.buttons = self.target_joy.buttons
        self.last_joy = joy

        new_twist = Twist()

        new_twist.linear.x = joy.axes[4] * 2
        new_twist.linear.y = joy.axes[3] * 2
        new_twist.linear.z = 0

        new_twist.angular.x = 0
        new_twist.angular.y = 0
        new_twist.angular.z = joy.axes[0] * 2

        self.twist_publisher.publish(new_twist)

        self.last_send_time = t_now


if __name__ == "__main__":
    joystick = PS4_controller(rate = 30)
    joystick.run()
