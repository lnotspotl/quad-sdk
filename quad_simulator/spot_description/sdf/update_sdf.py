#!/usr/bin/env python

import os

def main():
	os.system("gz sdf -p ../urdf/spot.urdf > ./spot.sdf")
	os.system("sed -i -e 's/spot_description//g' ./spot.sdf")

	os.system("gz sdf -p ../urdf/spot_with_camera.urdf > ./spot_with_camera.sdf")
	os.system("sed -i -e 's/spot_description//g' ./spot_with_camera.sdf")

if __name__ == "__main__":
	main()